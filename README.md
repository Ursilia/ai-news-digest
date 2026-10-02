# AI News Digest — Backend

Backend service for aggregating and summarizing news through LLM.

## Stack
- Python 3.13, FastAPI, Pydantic
- PostgreSQL + SQLAlchemy + Alembic
- JWT authentication (pyjwt, bcrypt)
- pytest for testing
- Docker for local development

## Architecture
Layered: `routes → services → repositories → models`,
with per-domain routing (`routes/auth.py`, `routes/sources.py`, `routes/tags.py`),
custom exception handling, and centralized error responses.

## Features
- User registration & JWT-based authentication
- Per-user data ownership (multi-tenant): each user only sees their own sources
- Full CRUD for news sources and tags
- Automated migrations via Alembic
- Test suite covering auth flows

## Run locally

Prerequisites: Docker, Python 3.13, Git

```bash
git clone <repo-url>
cd <repo>
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
cp .env.example .env         # then edit .env with your JWT_SECRET_KEY
docker-compose up -d
alembic upgrade head
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs

## Testing
```bash
# Create test database first:
# In DBeaver: CREATE DATABASE news_digest_test;
pytest -v
```

## Status
Work in progress. Currently implemented:
- Layered CRUD for sources and tags
- User authentication (register/login/JWT)
- Per-user data ownership
- Database migrations
- Basic auth test coverage

## AI Features

- `POST /ai/summarize` — summarize any text via LLM (gpt-4o-mini)
- `POST /ai/ask` — Q&A with conversation history
- `POST /ai/ask/stream` — same as `/ai/ask` but with Server-Sent Events streaming

All AI endpoints:
- Require authentication (JWT)
- Use retry with exponential backoff on transient errors
- Have 30-second timeout
- Load prompts from `prompts/` folder (editable without code changes)

Planned: LLM integration for summarization, RAG pipeline with pgvector,
background tasks (Celery), Docker deployment, CI/CD.

## RAG (Retrieval-Augmented Generation)

Full RAG pipeline built without frameworks (no LangChain).

- `POST /documents` — upload text, automatic chunking + embeddings
- `POST /documents/search` — semantic search across your documents
- `POST /documents/ask` — RAG-based Q&A with source citations

Stack:
- OpenAI `text-embedding-3-small` for embeddings
- pgvector extension in Postgres for vector storage
- Cosine distance for similarity search
- Sentence-aware chunking with overlap (500 tokens per chunk, 100 overlap)
- Distance threshold (0.7) filters irrelevant results

Multi-tenant: each user only searches within their own documents.