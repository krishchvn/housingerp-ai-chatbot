import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models.chat import ChatRequest, ChatResponse
from chat import process_chat
from db.connection import test_connection, create_database_if_not_exists
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs on startup
    create_database_if_not_exists()
    test_connection()
    yield
    # Runs on shutdown (nothing needed)


app = FastAPI(title="HousingERP AI Chatbot API", version="1.0.0", lifespan=lifespan)

# CORS — allow React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok", "service": "housingerp-ai"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return await process_chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
