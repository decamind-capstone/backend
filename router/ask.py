from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import ConversationDB, ChatHistoryDB
from error.exceptions import MissingFieldData, ConversationNotFound
from datetime import datetime
from typing import List, Optional

from rag_pipeline.qa_chain import build_qa_chain
from rag_pipeline.retriever import load_retriever
from rag_pipeline.llm import load_llm
from rag_pipeline.config import VECTOR_DB_PATHS, EMBEDDING_MODELS

## 라우터 설정
router = APIRouter(prefix="/v1/ask", tags=["Ask"])

## 요청 스키마
class AskRequest(BaseModel):
    conversationId: Optional[int] = None
    question: str

## 응답 스키마
class AskResponse(BaseModel):
    answer: str
    sources: List[str]
    createdAt: datetime
    conversationId: int

## 질문 처리 함수
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

    # # Mock 답변 (추후 AI 연동)
    # answer = f"[Mock Answer] Response to: {request.question}"
    # sources = ["문서1.pdf", "문서2.txt"]
    # created_at = datetime.utcnow()

    # RAG 파이프라인 로딩하기
    llm = load_llm()
    retriever = load_retriever(
        collection_name='sff_8071',
        db_path=str(VECTOR_DB_PATHS["MSA"]),
        model_name=EMBEDDING_MODELS
    )
    qa_chain = build_qa_chain(llm, retriever)

    # 질문에 대한 응답을 생성
    result = qa_chain.invove({"query": request.question})
    answer = result['result']
    source_docs = result.get('source_documents', [])
    sources = [doc.metadata.get('section_code', 'Unknown') for doc in source_docs]

    created_at = datetime.utcnow()  # 응답이 언제 생성?

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
