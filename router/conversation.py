from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ConversationDB
from error.exceptions import MissingFieldData, ConversationNotFound, DuplicateConversationTitle
from datetime import datetime
from typing import List

# 라우터 정의
router = APIRouter(prefix="/v1/conversations", tags=["Conversations"])

# 요청/응답 스키마
class ConversationRequest(BaseModel):
    title: str

class ConversationResponse(BaseModel):
    conversationId: int
    title: str
    createdAt: datetime
    updatedAt: datetime

# 대화 존재 여부 검증 함수
def validate_conversation_access(conversation_id: int, db: Session):
    conversation = db.query(ConversationDB).filter(
        ConversationDB.CONVERSATION_ID == conversation_id
    ).first()
    if not conversation:
        raise ConversationNotFound()
    return conversation

# 대화 목록 조회
@router.get("/", response_model=dict)
async def get_conversations(db: Session = Depends(get_db)):
    conversations = db.query(ConversationDB).all()

    if not conversations:
        raise ConversationNotFound()

    response = [
        {
            "conversationId": conv.CONVERSATION_ID,
            "title": conv.TITLE,
            "createdAt": conv.CREATED_AT,
            "updatedAt": conv.UPDATED_AT
        } for conv in conversations
    ]

    return {
        "success": True,
        "response": response,
        "error": None
    }

# 새 대화 생성
@router.post("/", response_model=dict)
async def create_conversation(request: ConversationRequest, db: Session = Depends(get_db)):
    if not request.title:
        raise MissingFieldData(['title'])

    # 제목 중복 검사
    duplicate_conv = db.query(ConversationDB).filter(
        ConversationDB.TITLE == request.title
    ).first()
    if duplicate_conv:
        raise DuplicateConversationTitle()

    now = datetime.utcnow()
    new_conv = ConversationDB(TITLE=request.title, CREATED_AT=now, UPDATED_AT=now)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)

    return {
        "success": True,
        "response": {"conversationId": new_conv.CONVERSATION_ID},
        "error": None
    }

# 대화 제목 수정
@router.put("/{conversationId}", response_model=dict)
async def update_conversation(conversationId: int, request: ConversationRequest, db: Session = Depends(get_db)):
    conv = validate_conversation_access(conversationId, db)

    if conv.TITLE == request.title:
        raise DuplicateConversationTitle()

    conv.TITLE = request.title
    conv.UPDATED_AT = datetime.utcnow()
    db.commit()
    db.refresh(conv)

    return {
        "success": True,
        "response": {"conversationId": conv.CONVERSATION_ID},
        "error": None
    }

# 대화 삭제
@router.delete("/{conversationId}", response_model=dict)
async def delete_conversation(conversationId: int, db: Session = Depends(get_db)):
    conv = validate_conversation_access(conversationId, db)
    db.delete(conv)
    db.commit()

    return {
        "success": True,
        "response": {"message": "대화 삭제 완료"},
        "error": None
    }
