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

from operator import itemgetter
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sqlalchemy import URL
from langchain_community.agent_toolkits import create_sql_agent


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
        print(doc)
        documentString = documentString + "Website chunk --- " + (doc[0].page_content) + " --- "


    embeddings = OpenAIEmbeddings()

    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        #("system", "You are a bot designed to parse information from several chunks of text from websites, giving an answer to a given question or statement. You must only use information from the chunks themselves and not come up with any information on your own. If the answer isn't found within the chunks, reply with 'Sorry, this is outside the scope of my information' rather than making up an answer."),
        ("system", "Parse information from several chunks of text from websites to answer a question or statement. Only use information from the chunks themselves and not come up with any information on your own. If the answer isn't found within the chunks, reply with 'Sorry, this is outside the scope of my information' rather than making up an answer. Make sure to include all relevant information."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": "Question: "+queryToMatch+" Information: "+documentString}))


def simplifyMessageHistory(messageHistory):
    load_dotenv()
    embeddings = OpenAIEmbeddings()
    messageHistory = "---".join(messageHistory)
    #print(messageHistory)

    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        #("system", "You are a bot designed to take a series of in order messages, seperated by ---, between a student and a chatbot and return a simplified question based on the most recent message. If the last message relates to previous messages sent, you should take that into account when forming the simplified request. You must only use information from the messages themselves and not come up with any information on your own."),
        ("system", "Based on this series of messages between a user and a chatbot, what is the latest thing the user is asking? Only say the answer and nothing else."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": messageHistory}))

def generateMYSQLReq(toMakeSQL):
    load_dotenv()
    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot designed to write a mysql request based on an question or statement for the 'events' table on the 'websites' database."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": toMakeSQL}))

def getNonVectorizedData(message):
 
    load_dotenv()

    #--
    from langchain_community.utilities import SQLDatabase

    POSTGRES_URI = os.getenv("POSTGRES_URI")

    # We dont want any other tables (for now) to be able to be queried
    include_tables = ["events", "societies"]

    db = SQLDatabase.from_uri(POSTGRES_URI, include_tables=include_tables)

    #--


    from langchain_community.agent_toolkits import create_sql_agent
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)

    #---

    #agent_executor.invoke(
    #    "List the total sales per country. Which country's customers spent the most?"
    #)

    #--

    examples = [
        {"input": "Give me more information about Shakespeare Society.", "query": "SELECT * FROM Socities WHERE Name='Shakespeare';"},
        {"input": "Give me more information about Skate Society.", "query": "SELECT * FROM Socities WHERE Name='Skate Socieity';"},
        {
            "input": "List all tracks that are longer than 5 minutes.",
            "query": "SELECT * FROM Track WHERE Milliseconds > 300000;",
        },
        
    ]


    from langchain_community.vectorstores import FAISS
    from langchain_core.example_selectors import SemanticSimilarityExampleSelector
    from langchain_openai import OpenAIEmbeddings

    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        FAISS,
        k=1, #this should be increased when we have more examples
        input_keys=["input"],
    )

    from langchain_core.prompts import (
        ChatPromptTemplate,
        FewShotPromptTemplate,
        MessagesPlaceholder,
        PromptTemplate,
        SystemMessagePromptTemplate,
    )

    system_prefix = """You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the given tools. Only use the information returned by the tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    If the question does not seem related to the database, just return "I don't know" as the answer.

    Here are some examples of user inputs and their corresponding SQL queries:"""

    few_shot_prompt = FewShotPromptTemplate(
        example_selector=example_selector,
        example_prompt=PromptTemplate.from_template(
            "User input: {input}\nSQL query: {query}"
        ),
        input_variables=["input", "dialect", "top_k"],
        prefix=system_prefix,
        suffix="",
    )

    full_prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessagePromptTemplate(prompt=few_shot_prompt),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    prompt_val = full_prompt.invoke(
        {
            "input": message,
            "top_k": 5,
            "dialect": "SQLite",
            "agent_scratchpad": [],
        }
    )
    print(prompt_val.to_string())

    agent = create_sql_agent(
        llm=llm,
        db=db,
        prompt=full_prompt,
        verbose=True,
        agent_type="openai-tools",
    )

    #agent.invoke({"input": "How many artists are there?"})

    import ast
    import re


    def query_as_list(db, query):
        res = db.run(query)
        res = [el for sub in ast.literal_eval(res) for el in sub if el]
        res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
        return list(set(res))

    ##Change this if needed
    societies = query_as_list(db, "SELECT Name FROM Societies")

    from langchain.agents.agent_toolkits import create_retriever_tool

    vector_db = FAISS.from_texts(societies, OpenAIEmbeddings())
    retriever = vector_db.as_retriever(search_kwargs={"k": 5})
    description = """Use to look up values to filter on. Input is an approximate spelling of the proper noun, output is \
    valid proper nouns. Use the noun most similar to the search."""
    retriever_tool = create_retriever_tool(
        retriever,
        name="search_proper_nouns",
        description=description,
    )

    system = """You are an agent designed to interact with a SQL database.
    Given an input question, create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
    Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most {top_k} results.
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for the relevant columns given the question.
    You have access to tools for interacting with the database.
    Only use the given tools. Only use the information returned by the tools to construct your final answer.
    You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

    DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

    If you need to filter on a proper noun, you must ALWAYS first look up the filter value using the "search_proper_nouns" tool! 

    You have access to the following tables: {table_names}"""

    prompt = ChatPromptTemplate.from_messages(
        [("system", system), ("human", "{input}"), MessagesPlaceholder("agent_scratchpad")]
    )
    agent = create_sql_agent(
        llm=llm,
        db=db,
        extra_tools=[retriever_tool],
        prompt=prompt,
        agent_type="openai-tools",
        verbose=False, #can change to true for debugging
    )

    response = agent.invoke({"input": message})
    return response   


def beautify(messageToSimplify):
    load_dotenv()
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
    load_dotenv()
    simplifiedRequest = simplifyMessageHistory(message)
    #print(simplifiedRequest)
    vectorizedReturn = getVectorizedData(simplifiedRequest)
    #print(vectorizedReturn)
    nonVectorizedReturn = getNonVectorizedData(simplifiedRequest)
    #if ((vectorizedReturn =! False) and (nonVectorizedReturn =! False)):
    #    return merge(beautify(vectorizedReturn), beautify(nonVectorizedReturn))
    responseToUser = beautify(vectorizedReturn)
    #print(responseToUser)
    return responseToUser




#todo:
#make it so that the url of the ource website is referenced after a piece of the the response it created
#to do this, you'll have to update the search function to also get the url and return it to documents. Add it to the end of each string before --- website chunk --- 

#question = "what sports events are happening in july?"
#docsToGive = (getMatchedVector(question))
#print(doGPTRequest(question, docsToGive))
#print(generateMYSQLReq(question))
#print(getVectorizedData("Retrieve every module in business"))
print(gptPipeline('{ "Messages":["Hello! How can I help?", "What modules are available for computer science?", "I dont know the answer to that.", "what module is CMD213"]}'))

