# AI News Digest

Backend service for aggregating and summarizing news through LLM (in progress).

## Stack
- Python 3.13, FastAPI, Pydantic

## Run
bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install fastapi "uvicorn[standard]"
uvicorn main:app --reload
