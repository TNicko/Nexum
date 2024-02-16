from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.db.supabase import create_supabase_client

app = FastAPI()

supabase = create_supabase_client()

origins = ["http://localhost:5173", "localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {"message": "hello world!"}


class CreateMessage(BaseModel):
    id: int
    message: str


@app.post("/api/query")
async def query(request: CreateMessage) -> CreateMessage:
    print(request)

    return request
