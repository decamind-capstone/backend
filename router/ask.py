from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ConversationDB, ChatHistoryDB
from error.exceptions import MissingFieldData, ConversationNotFound
from datetime import datetime
from typing import List, Optional

router = APIRouter(prefix="/v1/ask", tags=["Ask"])

class AskRequest(BaseModel):
    conversationId: Optional[int] = None
    question: str

class AskResponse(BaseModel):
    answer: str
    sources: List[str]
    createdAt: datetime
    conversationId: int

@router.post("/", response_model=dict)
async def ask_question(request: AskRequest, db: Session = Depends(get_db)):
    if not request.question:
        raise MissingFieldData(['question'])

    # 대화 존재 여부 확인 또는 새 대화 생성
    if not request.conversationId:
        now = datetime.utcnow()
        new_conv = ConversationDB(TITLE="New Conversation", CREATED_AT=now, UPDATED_AT=now)
        db.add(new_conv)
        db.commit()
        db.refresh(new_conv)
        conv_id = new_conv.CONVERSATION_ID
    else:
        conv = db.query(ConversationDB).filter(ConversationDB.CONVERSATION_ID == request.conversationId).first()
        if not conv:
            raise ConversationNotFound()
        conv.UPDATED_AT = datetime.utcnow()
        db.commit()
        conv_id = conv.CONVERSATION_ID

    # Mock 답변 (추후 AI 연동)
    answer = f"[Mock Answer] Response to: {request.question}"
    sources = ["문서1.pdf", "문서2.txt"]
    created_at = datetime.utcnow()

    # 히스토리 저장
    new_chat = ChatHistoryDB(CONVERSATION_ID=conv_id, QUESTION=request.question, ANSWER=answer, CREATED_AT=created_at)
    db.add(new_chat)
    db.commit()

    return {
        "success": True,
        "response": AskResponse(
            answer=answer,
            sources=sources,
            createdAt=created_at,
            conversationId=conv_id
        ).dict(),
        "error": None
    }
