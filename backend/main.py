from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.staticfiles import StaticFiles


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None


def build_app() -> FastAPI:
    app = FastAPI(title="Resume Assistant")

    # CORS: keep permissive for local dev; tighten for prod if needed.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/api/chat")
    async def chat(payload: ChatRequest) -> dict[str, str]:
        # Placeholder response until Phase 2c (model integration).
        return {
            "reply": (
                "Hi! The backend is wired up. "
                "Once Anthropic is connected, I'll answer using Dakota's resume."
            )
        }

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

