from fastapi import APIRouter, HTTPException

from models.chat import ChatRequest, ChatResponse
from services.chat_service import process_chat

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "service": "housingerp-ai"}


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        return await process_chat(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
