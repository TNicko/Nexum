import asyncio
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, UploadFile, Form
from fastapi.responses import JSONResponse, StreamingResponse
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
from pydantic import BaseModel
from app.db.supabase import create_supabase_client
from app.gpt.pipeline import gptPipeline
from typing import AsyncIterable, Awaitable

app = FastAPI()
supabase = create_supabase_client()

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

async def send_message(message: str) -> AsyncIterable[str]:
    callback = AsyncIteratorCallbackHandler()
    model = ChatOpenAI(
        streaming=True,
        verbose=True,
        callbacks=[callback]
    )
    
    async def wrap_done(fn: Awaitable, event: asyncio.Event):
        """Wrap an awaitable with an event to signal when it's done or an exception is raised."""
        try:
            await fn
        except Exception as e:
            # TODO: handle exception
            print(f"Caught exception: {e}")
        finally:
            # Signal the aiter to stop
            event.set()

    # Begin a task that runs in the background
    task = asyncio.create_task(wrap_done(
        model.agenerate(messages=[[HumanMessage(content=message)]]),
        callback.done),
    )

    async for token in callback.aiter():
        yield f"data: {token}\n\n"

    await task

@app.post("/api/query")
async def query(request: CreateQuery):
    print(request)
    messages = [message["text"] for message in request.chat]
    messages.append(request.message)
    response = gptPipeline(supabase, messages)
    print(response)
    return StreamingResponse(
        send_message(request.message), media_type="text/event-stream"
    )
    
