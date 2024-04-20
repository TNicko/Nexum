from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from app.gpt.pipeline import GPTPipeline
from typing import AsyncIterable, Awaitable

app = FastAPI()

origins = ["http://localhost:5173", "http://127.0.0.1:5173", "http://0.0.0.0:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CreateQuery(BaseModel):
    message: str
    chat: list


@app.post("/api/query")
async def query(request: CreateQuery):
    messages = [message["text"] for message in request.chat]
    messages.append(request.message)
    pipeline = GPTPipeline(streaming=True)
    return StreamingResponse(
        pipeline.stream_response(messages), media_type="text/event-stream"
    )
    
