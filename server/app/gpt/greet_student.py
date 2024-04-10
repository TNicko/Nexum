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


def getVectorizedData(queryToMatch):
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
    query = queryToMatch
    # k : number of retrieved results
    # filter : metadata to filer responses
    matched_docs = vstore.similarity_search_with_relevance_scores(
        query=query, k=5, filter=None
    )
    #for doc in matched_docs:
    #    print(f"{type(doc)}\n")
    #    print(f"{doc}\n")
    documentString = ""
    for doc in matched_docs:
        documentString = documentString + "Website chunk --- " + (doc[0].page_content) + " --- "


    embeddings = OpenAIEmbeddings()

    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot designed to parse information from several chunks of text from websites, giving an answer to a given question or statement. You must only use information from the chunks themselves and not come up with any information on your own. If the answer isn't found within the chunks, reply with 'Sorry, this is outside the scope of my information' rather than making up an answer."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": "Question: "+queryToMatch+" Information: "+documentString}))


def simplifyMessageHistory(messageHistory):
    embeddings = OpenAIEmbeddings()
    messageHistory = "---".join(messageHistory)
    #print(messageHistory)

    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot designed to take a series of in order messages, seperated by ---, between a student and a chatbot and return a simplified question based on the most recent message. If the last message relates to previous messages sent, you should take that into account when forming the simplified request. You must only use information from the messages themselves and not come up with any information on your own."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": messageHistory}))

def generateMYSQLReq(toMakeSQL):
    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot designed to write a mysql request based on an question or statement for the 'events' table on the 'websites' database."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": toMakeSQL}))

def beautify(messageToSimplify):
    embeddings = OpenAIEmbeddings()
    #print(messageHistory)

    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot designed to simplify a given piece of data into a more readable form if possible. If there is duplicate information, you should remove it. You must only use information from the messages themselves and not come up with any information on your own."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": messageToSimplify}))

# 1 - convert string of messages into final (last) request
# 2 - determine which servers need to be accessed in independent functions, returning data to this function
# 3 - combine the data returned and make it nicer
# 4 - return result to client

def gptPipeline(message):
    simplifiedRequest = simplifyMessageHistory(message)
    #print(simplifiedRequest)
    vectorizedReturn = getVectorizedData(simplifiedRequest)
    #nonVectorizedReturn = getNonVectorizedData(simplifiedRequest)
    #if ((vectorizedReturn =! False) and (nonVectorizedReturn =! False)):
    #    return merge(beautify(vectorizedReturn), beautify(nonVectorizedReturn))
    responseToUser = beautify(vectorizedReturn)
    print(responseToUser)
    return responseToUser




#todo:
#make it so that the url of the ource website is referenced after a piece of the the response it created
#to do this, you'll have to update the search function to also get the url and return it to documents. Add it to the end of each string before --- website chunk --- 

question = "what sports events are happening in july?"
#docsToGive = (getMatchedVector(question))
#print(doGPTRequest(question, docsToGive))
print(generateMYSQLReq(question))
#print(getMatched("Retrieve every module in business"))
#print(gptPipeline('{ "Messages":["Hello! How can I help?", "What modules are available for computer science?", "I dont know the answer to that.", "whos the head of the uni?"]}'))

