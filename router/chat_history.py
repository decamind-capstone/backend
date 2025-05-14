from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ChatHistoryDB
from error.exceptions import ConversationNotFound
from typing import List
from datetime import datetime

router = APIRouter(prefix="/v1/history", tags=["Chat History"])

class HistoryResponse(BaseModel):
    question: str
    answer: str
    createdAt: datetime

@router.get("/", response_model=dict)
async def get_history(conversationId: int, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    chats = db.query(ChatHistoryDB).filter(ChatHistoryDB.CONVERSATION_ID == conversationId).offset(offset).limit(limit).all()

    if not chats:
        raise ConversationNotFound()

    response = [
        HistoryResponse(
            question=chat.QUESTION,
            answer=chat.ANSWER,
            createdAt=chat.CREATED_AT
        ).dict() for chat in chats
    ]

    return {
        "success": True,
        "response": response,
        "error": None
    }
