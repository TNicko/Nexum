from openai import OpenAI
import json
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
import os

from supabase import create_client, Client

import vecs
from vecs.adapter import Adapter, ParagraphChunker, TextEmbedding
import tiktoken

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from dotenv import load_dotenv

from langchain.chains.query_constructor.base import AttributeInfo
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain_openai import OpenAI

from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query, UploadFile, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.db.supabase import create_supabase_client
from app.gpt.greet_student import gptPipeline



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
    message: list


@app.post("/api/query")
async def query(request: CreateMessage):
    #print(request)
    response = gptPipeline(request.message)

    return response
