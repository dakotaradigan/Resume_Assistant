# Resume Assistant

An AI-powered chatbot showcasing Dakota Radigan's professional experience, skills, and projects.

## Tech Stack

**Backend:**
- FastAPI (REST API)
- Claude 
- Qdrant (Vector search)

**Frontend:**
- Vanilla JavaScript (modular architecture)
- Custom CSS (Claude-inspired UI)

## Project Phases

- **Phase 1**: Foundation & Data Structure (Complete)
- **Phase 2**: Basic Chat with fetch() (REST API) (In Progress)
- **Phase 3**: Vector Search (RAG) (Pending)
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
cp .env.example .env
# Edit .env with your API keys
uvicorn main:app --reload
```

### Frontend

Open `frontend/index.html` in a browser, or serve with:

```bash
cd frontend
python3 -m http.server 3000
```

## Development

See `CLAUDE.md` for detailed development guide and architecture decisions.
