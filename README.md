# AI News Digest — Backend

Backend service for aggregating and summarizing news through LLM.

## Stack
- Python 3.13, FastAPI, Pydantic
- PostgreSQL + SQLAlchemy + Alembic
- Docker (Postgres via docker-compose)

## Architecture
Layered: `routes → services → repositories → models`, 
with custom exception handling and centralized error responses.

## Run locally

Prerequisites: Docker, Python 3.13, Git

```bash
git clone <repo-url>
cd <repo>
python -m venv .venv
.venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
docker-compose up -d
alembic upgrade head
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs

## Status
Work in progress. Currently implemented:
- CRUD for news sources and tags
- Layered architecture with repositories
- Centralized error handling (404, 409, 400)
- Database migrations via Alembic

Planned: authentication (JWT), LLM integration, RAG pipeline, 
background tasks (Celery), Docker deployment, CI/CD.