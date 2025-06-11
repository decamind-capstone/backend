from sqlalchemy import Column, String, DateTime, ForeignKey, BigInteger, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from db.database import engine
from datetime import datetime

Base = declarative_base()

# Conversation (대화 관리 테이블)
class ConversationDB(Base):
    __tablename__ = "CONVERSATION"

    CONVERSATION_ID = Column(BigInteger, primary_key=True, autoincrement=True)
    TITLE = Column(String(255), nullable=False, default="New Conversation")
    CREATED_AT = Column(DateTime, nullable=False, default=datetime.utcnow)
    UPDATED_AT = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    histories = relationship("ChatHistoryDB", back_populates="conversation", cascade="all, delete-orphan")


# ChatHistory (질문/답변 히스토리)
class ChatHistoryDB(Base):
    __tablename__ = "CHAT_HISTORY"

    HISTORY_ID = Column(BigInteger, primary_key=True, autoincrement=True)
    CONVERSATION_ID = Column(BigInteger, ForeignKey("CONVERSATION.CONVERSATION_ID", ondelete="CASCADE"), nullable=False)
    QUESTION = Column(Text, nullable=False)
    ANSWER = Column(Text, nullable=False)
    CREATED_AT = Column(DateTime, nullable=False, default=datetime.utcnow)
    IS_BOOKMARKED = Column(Boolean, default=False)

    conversation = relationship("ConversationDB", back_populates="histories")  
    

# 매퍼 적용
Base.metadata.create_all(bind=engine)
