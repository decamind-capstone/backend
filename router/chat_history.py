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
    historyId: int
    question: str
    answer: str
    isBookmarked: bool
    createdAt: datetime

# 대화 기준 히스토리 조회
@router.get("/", response_model=dict)
async def get_history(conversationId: int, limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    chats = db.query(ChatHistoryDB)\
              .filter(ChatHistoryDB.CONVERSATION_ID == conversationId)\
              .offset(offset).limit(limit).all()

    if not chats:
        raise ConversationNotFound()

    response = [
        {
            "historyId": chat.HISTORY_ID,
            "question": chat.QUESTION,
            "answer": chat.ANSWER,
            "isBookmarked": chat.IS_BOOKMARKED,
            "createdAt": chat.CREATED_AT
        } for chat in chats
    ]

    return {
        "success": True,
        "response": response,
        "error": None
    }

# 질문 찜 토글
@router.put("/{history_id}/bookmark", response_model=dict)
async def toggle_bookmark(history_id: int, db: Session = Depends(get_db)):
    history = db.query(ChatHistoryDB).filter(ChatHistoryDB.HISTORY_ID == history_id).first()
    if not history:
        raise HTTPException(status_code=404, detail="History not found")

    history.IS_BOOKMARKED = not history.IS_BOOKMARKED
    db.commit()
    db.refresh(history)

    return {
        "success": True,
        "response": {"historyId": history.HISTORY_ID, "isBookmarked": history.IS_BOOKMARKED},
        "error": None
    }

# 전체 찜 질문만 모아서 반환
@router.get("/bookmarked", response_model=dict)
async def get_bookmarked_history(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    bookmarked_chats = db.query(ChatHistoryDB)\
                         .filter(ChatHistoryDB.IS_BOOKMARKED == True)\
                         .order_by(ChatHistoryDB.CREATED_AT.desc())\
                         .offset(offset).limit(limit).all()

    response = [
        {
            "historyId": chat.HISTORY_ID,
            "question": chat.QUESTION,
            "answer": chat.ANSWER,
            "isBookmarked": chat.IS_BOOKMARKED,
            "createdAt": chat.CREATED_AT
        } for chat in bookmarked_chats
    ]

    return {
        "success": True,
        "response": response,
        "error": None
    }
