# HousingERP AI Chatbot

An AI-powered chatbot embedded into the HousingERP platform, enabling residents to raise complaints through plain text and query their complaint history using natural language.

## Quick Start

### Backend
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # fill in GROQ_API_KEY and DATABASE_URL
python db/run_schemas.py    # initialise Supabase tables
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env        # set VITE_API_BASE=https://housingerp-ai-chatbot.onrender.com
npm run dev                 # runs on http://localhost:5173
```

## Project Structure

```
housingerp-ai/
├── README.md
├── docs/                   # Full project documentation
├── backend/                # FastAPI + Python
│   ├── main.py
│   ├── routers/
│   ├── services/
│   ├── models/
│   └── db/
└── frontend/               # React + TypeScript + Vite
    └── src/
```

## Documentation

See [`docs/`](./docs/index.md) for full documentation including architecture, API reference, data flows, and test scenarios.

## Tech Stack Summary

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | FastAPI, Python 3.11                |
| LLM       | Groq API (llama-3.3-70b-versatile)  |
| Database  | Supabase (PostgreSQL)               |
| ORM       | SQLAlchemy 2.0 (sync, psycopg2)     |
| Frontend  | React 18, TypeScript, Vite          |
| HTTP      | Axios                               |
