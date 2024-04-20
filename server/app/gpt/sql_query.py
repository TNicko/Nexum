import os
import ast
import re
import app.gpt.system_prompts as sp
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

POSTGRES_URI = os.getenv("POSTGRES_URI")
QUERY_TABLES = ["events", "societies"]

EXAMPLES = [
    {
        "input": "Give me more information about Shakespeare Society.",
        "query": "SELECT * FROM Socities WHERE Name='Shakespeare';",
    },
    {
        "input": "Give me more information about Skate Society.",
        "query": "SELECT * FROM Socities WHERE Name='Skate Socieity';",
    },
    {
        "input": "List all tracks that are longer than 5 minutes.",
        "query": "SELECT * FROM Track WHERE Milliseconds > 300000;",
    },
]


class SQLQueryAgent:
    def __init__(self, llm=None, embeddings=None):
        self.db = SQLDatabase.from_uri(
            POSTGRES_URI, include_tables=QUERY_TABLES
        )
        self.llm = (
            llm if llm else ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        )
        self.embeddings = embeddings if embeddings else OpenAIEmbeddings()
        self.retriever_tool = self._set_retriever()
        self.example_selector = (
            SemanticSimilarityExampleSelector.from_examples(
                EXAMPLES, self.embeddings, FAISS, k=1, input_keys=["input"]
            )
        )

        self.few_shot_prompt = FewShotPromptTemplate(
            example_selector=self.example_selector,
            example_prompt=PromptTemplate.from_template(
                "User input: {input}\nSQL query: {query}"
            ),
            input_variables=["input", "dialect", "top_k"],
            prefix=sp.SQL_RSP_PROMPT_PREFIX,
            suffix="",
        )

        self.full_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessagePromptTemplate(prompt=self.few_shot_prompt),
                ("human", "{input}"),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )

        self.agent = create_sql_agent(
            llm=self.llm,
            db=self.db,
            extra_tools=[self.retriever_tool],
            prompt=self.full_prompt,
            agent_type="openai-tools",
            verbose=False,
        )

    def _set_retriever(self):
        def query_as_list(query):
            res = self.db.run(query)
            res = [el for sub in ast.literal_eval(res) for el in sub if el]
            res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
            return list(set(res))

        # Change this if needed
        societies = query_as_list("SELECT Name FROM Societies")

        vector_db = FAISS.from_texts(societies, self.embeddings)
        retriever = vector_db.as_retriever(search_kwargs={"k": 5})
        description = """
        Use to look up values to filter on. Input is an approximate spelling 
        of the proper noun, output is valid proper nouns. Use the noun most 
        similar to the search.
        """
        retriever_tool = create_retriever_tool(
            retriever,
            name="search_proper_nouns",
            description=description,
        )
        return retriever_tool

    def process(self, message: str):
        response = self.agent.invoke({"input": message})
        return response["output"]
