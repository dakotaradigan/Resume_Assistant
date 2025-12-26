from __future__ import annotations

import json
import logging
import time
from collections import defaultdict
from pathlib import Path
from functools import lru_cache
from uuid import uuid4

from anthropic import Anthropic
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles

from config import get_settings

logger = logging.getLogger("resume-assistant")

# Keep richer context: up to ~15 turns (user+assistant), then compact earlier history.
MAX_SESSION_MESSAGES = 40
COMPACT_AFTER = 30
COMPACT_KEEP_RECENT = 20
COMPACT_CHAR_LIMIT = 1200

# Scalability: In-memory storage (easy to swap to Redis later)
SESSION_MESSAGES: dict[str, list[dict]] = {}
SESSION_METADATA: dict[str, dict] = {}  # Track creation time, last access
RATE_LIMIT_TRACKER: dict[str, list[float]] = defaultdict(list)  # Session -> [timestamps]


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


# === Scalability Helper Functions ===


def _check_rate_limit(session_id: str) -> bool:
    """
    Rate limiting: Allow max N requests per minute per session.
    Returns True if request is allowed, False if rate limit exceeded.

    Migration path: Replace with Redis-based rate limiting when scaling.
    """
    settings = get_settings()
    now = time.time()
    window = 60.0  # 1 minute window

    # Get recent request timestamps for this session
    timestamps = RATE_LIMIT_TRACKER[session_id]

    # Remove timestamps older than the window
    timestamps[:] = [ts for ts in timestamps if now - ts < window]

    # Check if limit exceeded
    if len(timestamps) >= settings.rate_limit_requests_per_minute:
        return False

    # Add current request timestamp
    timestamps.append(now)
    return True


def _cleanup_old_sessions() -> None:
    """
    Session cleanup: Remove sessions older than max age to prevent memory leaks.
    Runs on each request (lightweight check).

    Migration path: Use Redis TTL for automatic expiration when scaling.
    """
    settings = get_settings()
    now = time.time()
    max_age = settings.session_max_age_seconds

    # Find expired sessions
    expired = [
        sid for sid, meta in SESSION_METADATA.items()
        if now - meta.get("last_access", 0) > max_age
    ]

    # Clean up expired sessions
    for sid in expired:
        SESSION_MESSAGES.pop(sid, None)
        SESSION_METADATA.pop(sid, None)
        RATE_LIMIT_TRACKER.pop(sid, None)

    if expired:
        logger.info(f"Cleaned up {len(expired)} expired sessions")


def _update_session_metadata(session_id: str) -> None:
    """Track session creation and last access time for cleanup."""
    now = time.time()
    if session_id not in SESSION_METADATA:
        SESSION_METADATA[session_id] = {"created_at": now, "last_access": now}
    else:
        SESSION_METADATA[session_id]["last_access"] = now


# === Data Loading Functions ===


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError(f"File not found: {path}") from exc
    except OSError as exc:
        raise RuntimeError(f"Unable to read file: {path}") from exc


def _format_resume_context(data: dict) -> str:
    lines: list[str] = []
    personal = data.get("personal", {})
    if personal:
        name = personal.get("name", "").strip()
        title = personal.get("title", "").strip()
        summary = personal.get("summary", "").strip()
        header = " - ".join([part for part in [name, title] if part])
        if header:
            lines.append(header)
        if summary:
            lines.append(summary)

    experiences = data.get("experience", [])
    if experiences:
        lines.append("Experience:")
        for exp in experiences:
            role = exp.get("role", "")
            company = exp.get("company", "")
            duration = exp.get("duration", "")
            achievements = exp.get("achievements", []) or []
            sample_achievements = "; ".join(achievements[:3])
            lines.append(
                f"- {role} at {company} ({duration}) — {sample_achievements}".strip()
            )

    projects = data.get("projects", [])
    if projects:
        lines.append("Projects:")
        for proj in projects:
            name = proj.get("name", "")
            tagline = proj.get("tagline", "")
            highlights = "; ".join((proj.get("highlights") or [])[:2])
            lines.append(
                f"- {name}: {tagline}".strip()
                + (f" — {highlights}" if highlights else "")
            )

    skills = data.get("skills", {})
    if skills:
        lines.append("Skills:")
        technical = skills.get("technical", []) or []
        if technical:
            lines.append(f"- Technical: {', '.join(technical)}")

    return "\n".join(lines)


@lru_cache(maxsize=1)
def load_system_prompt() -> str:
    settings = get_settings()
    return _read_text(settings.data_dir / "system_prompt.txt").strip()


@lru_cache(maxsize=1)
def load_resume_context() -> str:
    settings = get_settings()
    resume_path = settings.data_dir / "resume.json"
    try:
        data = json.loads(resume_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise RuntimeError(f"Resume data not found: {resume_path}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Resume data is not valid JSON: {resume_path}") from exc
    except OSError as exc:
        raise RuntimeError(f"Unable to read resume data: {resume_path}") from exc
    return _format_resume_context(data)


def _get_session_history(session_id: str) -> list[dict]:
    history = SESSION_MESSAGES.get(session_id)
    if history is None:
        history = []
        SESSION_MESSAGES[session_id] = history
    return history


def _append_session_message(session_id: str, role: str, text: str) -> None:
    history = _get_session_history(session_id)
    history.append({"role": role, "content": [{"type": "text", "text": text}]})
    _compact_session_history(session_id)


def _compact_session_history(session_id: str) -> None:
    history = _get_session_history(session_id)
    if len(history) <= COMPACT_AFTER:
        return

    early = history[:-COMPACT_KEEP_RECENT]
    recent = history[-COMPACT_KEEP_RECENT:]

    def _extract_text(msg: dict) -> str:
        parts = []
        for block in msg.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text", ""))
        return " ".join(parts).strip()

    summary_lines: list[str] = []
    for msg in early:
        role = msg.get("role", "unknown")
        text = _extract_text(msg)
        if text:
            summary_lines.append(f"{role.capitalize()}: {text}")

    summary_text = "\n".join(summary_lines)[:COMPACT_CHAR_LIMIT]
    summary_message = {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": (
                    "Earlier conversation summary (compacted for context):\n"
                    f"{summary_text}"
                ),
            }
        ],
    }

    new_history = [summary_message, *recent]
    if len(new_history) > MAX_SESSION_MESSAGES:
        new_history = new_history[-MAX_SESSION_MESSAGES:]

    SESSION_MESSAGES[session_id] = new_history


def build_app() -> FastAPI:
    app = FastAPI(title="Resume Assistant")
    settings = get_settings()

    # CORS: Environment-aware configuration
    # Development: Allow all origins for local testing
    # Production: Restrict to specific domain (update when deploying)
    if settings.environment == "production":
        # TODO: Update with your production domain before deploying
        allowed_origins = [
            "https://assistant.dakotaradigan.com",
            "https://dakotaradigan.com",
        ]
    else:
        # Development: Allow all origins (localhost, etc.)
        allowed_origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/chat")
    async def chat(payload: ChatRequest) -> ChatResponse:
        session_id = payload.session_id or str(uuid4())

        # === Scalability Guardrails ===

        # 1. Session cleanup: Remove old sessions periodically
        _cleanup_old_sessions()

        # 2. Update session metadata (tracks last access for cleanup)
        _update_session_metadata(session_id)

        # 3. Rate limiting: Prevent abuse
        if not _check_rate_limit(session_id):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Rate limit exceeded. Please wait a moment before sending "
                    "another message. This helps ensure fair access for all visitors."
                ),
            )

        # === Validation ===

        if not settings.anthropic_api_key:
            raise HTTPException(
                status_code=503,
                detail="Anthropic API key not configured. Set ANTHROPIC_API_KEY.",
            )

        try:
            system_prompt = load_system_prompt()
            resume_context = load_resume_context()
        except RuntimeError as exc:
            logger.exception("Failed to load prompt or resume data")
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        system_message = f"{system_prompt}\n\n[RESUME DATA]\n{resume_context}"

        # === API Call with Timeout ===

        # 4. API timeout: Prevent hanging requests
        client = Anthropic(
            api_key=settings.anthropic_api_key,
            timeout=settings.api_timeout_seconds,
        )

        try:
            history = _get_session_history(session_id)
            messages = [
                *history,
                {"role": "user", "content": [{"type": "text", "text": payload.message}]},
            ]

            response = client.messages.create(
                model=settings.anthropic_model,
                max_tokens=settings.anthropic_max_tokens,
                system=system_message,
                messages=messages,
            )
            reply_text = "".join(
                block.text for block in response.content if block.type == "text"
            )
        except Exception as exc:  # pragma: no cover - network errors / SDK issues
            logger.exception("Anthropic chat request failed")
            raise HTTPException(
                status_code=502,
                detail="Unable to process chat right now. Please try again soon.",
            ) from exc

        if not reply_text:
            reply_text = (
                "I couldn't generate a response just now. "
                "Please try asking in a different way."
            )

        _append_session_message(session_id, "user", payload.message)
        _append_session_message(session_id, "assistant", reply_text)

        return ChatResponse(reply=reply_text, session_id=session_id)

    # Serve the frontend files from ../frontend
    frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
    if frontend_dir.exists():
        app.mount(
            "/",
            StaticFiles(directory=frontend_dir, html=True),
            name="frontend",
        )

    return app


app = build_app()

