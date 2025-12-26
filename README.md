# Resume Assistant

An AI-powered chatbot showcasing Dakota Radigan's professional experience, skills, and projects.

## Tech Stack

**Backend:**
- FastAPI (REST API)
- Claude API
- Optional RAG (Qdrant + OpenAI embeddings)

**Frontend:**
- Vanilla JavaScript (modular architecture)
- Custom CSS (Claude-inspired UI)

## What’s Implemented

- **Chat API**: `POST /api/chat` (session-aware via `session_id`)
- **Frontend served by backend**: open `http://127.0.0.1:8000/`
- **Health checks**: `GET /health`, `GET /health/rag`
- **Safety/scalability guardrails**: memory-backed sessions, compaction, rate limiting
- **RAG retrieval (optional)**:
  - Uses Qdrant (remote endpoint via `QDRANT_URL`)
  - Uses OpenAI embeddings (`text-embedding-3-small`) when enabled

## Project Phases

- **Phase 1**: Foundation & Data Structure (Complete)
- **Phase 2**: Basic Chat with fetch() (REST API) (Complete)
- **Phase 3**: Vector Search (RAG) (Implemented; persistence optional)
- **Phase 4**: Multimodal Support (Images) (Pending)
- **Phase 5**: WebSocket (Optional) (Pending)
- **Phase 6**: Frontend Polish (Pending)
- **Phase 7**: Deployment (Pending)

## Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create backend/.env (see env vars below)
uvicorn main:app --reload
```

#### Required environment variables

Create `backend/.env` with at least:

```bash
ANTHROPIC_API_KEY=...
```

Optional (recommended):

```bash
# App behavior
ENVIRONMENT=development
DEBUG=false

# Model config
ANTHROPIC_MODEL=claude-opus-4-5-20251101
ANTHROPIC_MAX_TOKENS=2048

# Abuse protection
RATE_LIMIT_REQUESTS_PER_MINUTE=20
SESSION_MAX_AGE_SECONDS=3600
API_TIMEOUT_SECONDS=30
MAX_USER_MESSAGE_CHARS=2000

# Admin endpoint protection (required in production)
ADMIN_TOKEN=...
```

#### RAG (Qdrant Cloud)

RAG is enabled by default (`USE_RAG=true`). It requires embeddings + a Qdrant endpoint; configure:

- `USE_RAG=true`
- `OPENAI_API_KEY=...` (for embeddings)
- `QDRANT_URL=...` (required for RAG)
- `QDRANT_API_KEY=...` (optional; needed for Qdrant Cloud)

To disable RAG and always use the local `data/resume.json` context:

- `USE_RAG=false`

### Frontend

The backend serves the frontend at `/`, so the simplest workflow is:

- Start the backend (`uvicorn main:app --reload`)
- Open `http://127.0.0.1:8000/`

If you serve `frontend/` separately, you’ll need to ensure requests reach the backend (the frontend currently calls `fetch("/api/chat")`, i.e., same-origin).

```bash
cd frontend
python3 -m http.server 3000
```

## Development

See `CLAUDE.md` for detailed development guide and architecture decisions.

### Tests

Offline unit tests (no OpenAI key required):

```bash
python3 -m unittest discover -s backend -p "test_*.py"
```

Optional integration test (uses real OpenAI embeddings; keep it off by default):

```bash
RUN_INTEGRATION=1 OPENAI_API_KEY=... python3 -m unittest backend/test_rag.py
```
