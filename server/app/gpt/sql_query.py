import os
import ast
import re
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain.agents.agent_toolkits import create_retriever_tool
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from dotenv import load_dotenv

load_dotenv()

def getNonVectorizedData(message):

    POSTGRES_URI = os.getenv("POSTGRES_URI")

    # We dont want any other tables (for now) to be able to be queried
    include_tables = ["events", "societies"]

    db = SQLDatabase.from_uri(POSTGRES_URI, include_tables=include_tables)

    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    examples = [
    {"input": "Give me more information about Shakespeare Society.", "query": "SELECT * FROM Socities WHERE Name='Shakespeare';"},
    {"input": "Give me more information about Skate Society.", "query": "SELECT * FROM Socities WHERE Name='Skate Socieity';"},
    {
        "input": "List all tracks that are longer than 5 minutes.",
        "query": "SELECT * FROM Track WHERE Milliseconds > 300000;",
    },
    
    ]

    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        OpenAIEmbeddings(),
        FAISS,
        k=1, #this should be increased when we have more examples
        input_keys=["input"],
    )


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

    If you need to filter on a proper noun, you must ALWAYS first look up the filter value using the "search_proper_nouns" tool! 

    You have access to the following tables: {table_names}

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

    """
    prompt_val = full_prompt.invoke(
        {
            "input": message,
            "top_k": 5,
            "dialect": "SQLite",
            "table_names": "Societies",
            "agent_scratchpad": [],
        }
    )
    """
    agent = create_sql_agent(
        llm=llm,
        db=db,
        extra_tools=[retriever_tool],
        prompt=full_prompt,
        agent_type="openai-tools",
        verbose=True,
    )

    response = agent.invoke({"input": message})
    return response['output']   
