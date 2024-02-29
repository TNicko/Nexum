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


def getMatched(queryToMatch):
    load_dotenv()

    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    embeddings = OpenAIEmbeddings()

    vstore = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents",
    )
    # k : number of retrieved results
    # filter : metadata to filer responses
    matched_docs = vstore.similarity_search_with_relevance_scores(
        query=queryToMatch, k=10, filter=None
    )
    #for doc in matched_docs:
    #    print(f"{type(doc)}\n")
    #    #print(f"{doc[0].page_content}\n")
    documentString = ""
    for doc in matched_docs:
        documentString = documentString + "Website chunk --- " + (doc[0].page_content) + " --- "
    return documentString

def doGPTRequest(query, givenDocuments):
    loader = WebBaseLoader("https://docs.smith.langchain.com/overview")
    docs = loader.load()
    embeddings = OpenAIEmbeddings()


    exampleStudent = '{ "Name":"Jessica", "Subject":"Computer science"}'
    studentData = json.loads(exampleStudent)

    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot designed to parse information from several chunks of text from websites, giving an answer to a given question"),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": "Question: "+query+" Information: "+givenDocuments}))

def langchainRetrieveQuery():
    load_dotenv()

    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    embeddings = OpenAIEmbeddings()

    vstore = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="documents",
        query_name="match_documents",
    )
    metadata_field_info = [
        AttributeInfo(
            name="genre",
            description="The genre of the movie",
            type="string or list[string]",
        ),
        AttributeInfo(
            name="year",
            description="The year the movie was released",
            type="integer",
        ),
        AttributeInfo(
            name="director",
            description="The name of the movie director",
            type="string",
        ),
        AttributeInfo(
            name="rating", description="A 1-10 rating for the movie", type="float"
        ),
    ]
    document_content_description = "A chunk of text from a one of Loughborough Universities websites"
    llm = OpenAI(temperature=0)
    retriever = SelfQueryRetriever.from_llm(
        llm,
        vstore,
        document_content_description,
        metadata_field_info,
        enable_limit=True,
        verbose=True,
    )
    retriever.get_relevant_documents("what are two movies about dinosaurs")

question = "What modules are one the masters computer science course?"
docsToGive = (getMatched(question))
print(doGPTRequest(question, docsToGive))