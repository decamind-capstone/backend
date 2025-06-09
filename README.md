# backend-fastapi

# 📦 backend - RAG 기반 문서 검색 챗봇 (FastAPI)

기업 내 기술 문서 검색을 위한 RAG 기반 챗봇 백엔드입니다.  
LLM 기반 자연어 질문에 대해 관련 사내 문서를 검색하고, 응답을 생성해주는 역할을 합니다.

---

## ⚙️ 실행 방법

### 1. 프로젝트 폴더 이동

cd backend
### 2. 가상환경 실행

# PowerShell
.\venv\Scripts\Activate.ps1

# 또는 CMD
venv\Scripts\activate.bat

### 3. 패키지 설치

pip install -r requirements.txt

### 4. 도커로 MySQL 실행

docker-compose -f docker-compose-dev.yaml up -d

### 5. 서버 실행

uvicorn main:app --reload

### 6. Swagger 문서 접속

http://localhost:8000/docs

🔑 주요 API 경로
Endpoint	Method	설명
/v1/conversations/	POST	새 대화 생성
/v1/conversations/	GET	대화 목록 조회
/v1/conversations/{id}	PUT	대화 제목 수정
/v1/conversations/{id}	DELETE	대화 삭제
/v1/ask/	POST	질문 전송 (RAG 기반 응답)
/v1/history/{conversation_id}	GET	해당 대화의 질문/답변 히스토리 조회

📁 주요 폴더 및 파일 설명
main.py
FastAPI 앱 인스턴스를 생성하고 라우터를 등록합니다.

router/
API 엔드포인트들을 담당합니다:

conversation.py - 대화 생성, 조회, 수정, 삭제

ask.py - 질문 처리 (RAG 연동)

chat_history.py - 대화 히스토리 조회

db/
데이터베이스 연결 및 ORM 모델 정의:

database.py - SQLAlchemy 연결 설정

models.py - CONVERSATION / CHAT_HISTORY 테이블 정의

core/
앱 전역 설정 관리

config.py - .env 파일의 환경변수 불러오기

rag_pipeline/
RAG 구성 요소:

llm.py - LLM 로딩 및 HuggingFace 파이프라인 생성

retriever.py - 벡터 DB 로딩 및 LangChain QA 체인 설정

🐳 Docker 관련
docker-compose-dev.yaml
개발 환경용 MySQL 컨테이너 설정

init/schema.sql 파일로 DB 자동 초기화

Dockerfile (선택)
FastAPI 앱 도커 이미지로 패키징 시 사용

⚠️ 주의사항
.env 파일은 절대 깃허브에 올리지 마세요 (.gitignore에 등록됨)

서버 실행 전 Docker MySQL이 정상 실행되고 있는지 확인하세요.

SentencePiece, bitsandbytes, transformers 등의 의존성은 모델에 따라 추가 설치가 필요할 수 있습니다.

🤝 프론트엔드 연동 정보
프론트는 React 기반이며, 다음 API를 호출합니다:

/v1/conversations (생성/조회/수정/삭제)

/v1/ask (질문 전송)

/v1/history/{conversation_id} (히스토리 표시)

백엔드는 CORS 설정이 되어 있어 포트가 달라도 연동이 가능합니다.



