from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI()

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
async def query(message_fc: CreateMessage) -> CreateMessage:
    mc = ModelController()
    message = await mc.create_message(message_fc.dict())
    print(message)

    return message
