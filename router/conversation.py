from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ConversationDB, ChatHistoryDB
from error.exceptions import MissingFieldData, ConversationNotFound, DuplicateConversationTitle
from datetime import datetime
from typing import List
from rag_pipeline.llm import load_llm

# 라우터 정의
router = APIRouter(prefix="/v1/conversations", tags=["Conversations"])

# 요청/응답 스키마
class ConversationRequest(BaseModel):
    title: str = ""

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

# 새 대화 생성 (자동 제목 생성 포함)
@router.post("/", response_model=dict)
async def create_conversation(request: ConversationRequest, db: Session = Depends(get_db)):
    title = request.title.strip() if request.title else ""

    if title:
        # 중복 검사
        duplicate_conv = db.query(ConversationDB).filter(
            ConversationDB.TITLE == title
        ).first()
        if duplicate_conv:
            raise DuplicateConversationTitle()
    else:
        # 최근 1개 질문을 기반으로 제목 자동 생성
        recent_histories = db.query(ChatHistoryDB).order_by(ChatHistoryDB.CREATED_AT.desc()).limit(1).all()
        context = "\n".join([h.QUESTION for h in reversed(recent_histories)]) if recent_histories else "대화 시작"

        llm = load_llm()
        title = llm.invoke(f"다음 대화를 요약해서 제목을 10자 이내로 정리해줘:\n{context}")

    now = datetime.utcnow()
    new_conv = ConversationDB(TITLE=title, CREATED_AT=now, UPDATED_AT=now)
    db.add(new_conv)
    db.commit()
    db.refresh(new_conv)

    return {
        "success": True,
        "response": {
            "conversationId": new_conv.CONVERSATION_ID,
            "title": title
        },
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
