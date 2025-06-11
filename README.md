# 📦 backend-fastapi - RAG 기반 문서 검색 챗봇 (FastAPI)

기업 내 기술 문서를 효율적으로 검색하기 위한 **RAG 기반의 챗봇 백엔드**입니다.  
FastAPI, LangChain, HuggingFace 기반으로 구축되었으며,  
자연어 질문에 대해 관련 문서를 검색하고 응답을 생성합니다.

---

## ⚙️ 실행 방법

### 1. 프로젝트 폴더 이동

```bash
cd backend
```

### 2. 가상환경 실행

```bash
# PowerShell
.\venv\Scripts\Activate.ps1

# 또는 CMD
venv\Scripts\activate.bat
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. 도커로 MySQL 실행

```bash
docker-compose -f docker-compose-dev.yaml up -d
```

### 5. FastAPI 서버 실행

```bash
uvicorn main:app --reload
```

### 6. Swagger 문서 접속

[http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔑 주요 API 요약

| Endpoint                             | Method | 설명                                 |
|--------------------------------------|--------|--------------------------------------|
| `/v1/conversations/`                 | POST   | 새 대화 생성 (자동 요약 제목 포함)  |
| `/v1/conversations/`                 | GET    | 전체 대화 목록 조회                  |
| `/v1/conversations/{id}`             | PUT    | 대화 제목 수정                       |
| `/v1/conversations/{id}`             | DELETE | 대화 삭제                            |
| `/v1/ask/`                           | POST   | 질문 전송 (RAG 기반 응답 생성)      |
| `/v1/history/{conversation_id}`      | GET    | 특정 대화의 질문/답변 히스토리 조회 |
| `/v1/history/{history_id}/bookmark`  | PUT    | 질문/답변에 대한 찜 토글            |

---

## 📁 폴더 구조 및 역할

```
backend/
│
├── main.py                 # FastAPI 앱 실행 지점
├── router/                # API 라우터 모음
│   ├── conversation.py    # 대화 생성/조회/수정/삭제
│   ├── ask.py             # 질문 처리 (RAG 연동)
│   └── chat_history.py    # 대화 히스토리 및 찜 처리
│
├── db/                    # DB 연동 및 ORM 정의
│   ├── database.py        # SQLAlchemy DB 연결 설정
│   └── models.py          # CONVERSATION, CHAT_HISTORY 테이블 정의
│
├── rag_pipeline/          # RAG Pipeline 구성
│
├── core/
│   └── config.py          # .env 불러오기 설정
│
├── init/
│   └── schema.sql         # MySQL 초기 테이블 정의
```

---

## 🐳 Docker

- `docker-compose-dev.yaml`: MySQL 개발 컨테이너 실행 설정
- `init/schema.sql`: 최초 컨테이너 실행 시 DB 자동 생성
- `Dockerfile`: FastAPI 앱을 이미지화할 때 사용 (선택)

---

## ⚠️ 유의사항

- `.env` 파일은 절대 Git에 커밋되지 않도록 주의하세요. (`.gitignore` 포함)
- `bitsandbytes`, `sentencepiece`, `transformers` 등 일부 LLM 관련 패키지는 모델에 따라 별도 설치 필요
- 로컬 GPU 사용 시 `torch_dtype`, `device_map`, `bnb_config` 등을 환경에 맞게 조정해야 합니다.

---

## 🤝 프론트엔드 연동 정보

React 기반 UI와 연동되며, 다음 API를 호출합니다:

- `/v1/conversations` (사이드바 대화 목록 표시 및 생성)
- `/v1/ask` (질문 제출 → 응답 생성)
- `/v1/history/{conversation_id}` (채팅 히스토리 조회)
- `/v1/history/{history_id}/bookmark` (답변 즐겨찾기)

프론트와 백엔드는 CORS 설정이 완료되어 있어 다른 포트에서도 연동 가능합니다.

---

> 📌 모든 기능은 Swagger에서 직접 테스트 가능합니다.



