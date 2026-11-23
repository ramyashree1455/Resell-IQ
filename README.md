# ReSellIQ: An AI-Assisted Resale Marketplace

Resale marketplace where sellers go through an AI interview that produces a verified
condition grade (A to D), and a Chrome extension (ReSellIQ Lens) shows buyers a fair-price meter.

## Architecture

```
Web App (React)            Browser Extension (Lens)
        \                       /
          Backend API (FastAPI)
   Auth | Listings | Orders | Chat | Admin
   Interview (LLM + Vision) | Grading | Price Engine
        |               |               |
   PostgreSQL/SQLite  Image storage   Task queue
```

## Run the backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to try every endpoint in the browser.
Run tests: `cd backend && python -m pytest -q`

## Folders

| Folder | What | Owner |
|---|---|---|
| `backend/app/routers/` | one file per feature | see docs/TASK_SPLIT.md |
| `frontend/` | React web app | both (own pages) |
| `extension/` | Chrome MV3 extension (Lens) | Friend |
| `docs/` | task split, git guide | both |

## Design decisions (fill in as we go)
- FastAPI: Python makes AI integration easy.
- SQLite for development, PostgreSQL in production via `DATABASE_URL`.
- JWT auth with buyer / seller / admin roles.

## Limitations (fill in at the end)
