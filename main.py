from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from router import conversation, ask, chat_history

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], 
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.include_router(conversation.router)

app.include_router(ask.router)

app.include_router(chat_history.router)

# API Server Test
@app.get("/", status_code=status.HTTP_200_OK)
async def read_root():
    return {"Hello" : "World"}