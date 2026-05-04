import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers.chat import router as chat_router
from routers.complaints import router as complaints_router

load_dotenv()

app = FastAPI(title="HousingERP AI Chatbot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in os.getenv("CORS_ORIGINS", "https://housingerp-ai-chatbot-web.onrender.com").split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(complaints_router)
