import os
import app.gpt.system_prompts as sp
from app.gpt.agent_tools import EventEmbeddingTool, SocietyEmbeddingTool
from app.db.supabase import create_supabase_client
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.example_selectors.semantic_similarity import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
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
        "input": "I'm interested in societies related to classical theatre.",
        "query": "Use SocietyEmbeddingTool to find top 5 societies related to 'classical theatre'.",
    },
    {
        "input": "Find events related to modern art.",
        "query": "Use EventEmbeddingTool to find top 5 events related to 'modern art'.",
    },
    {
        "input": "What societies have events today?",
        "query": "SELECT * FROM public.events WHERE DATE(start_date) = CURRENT_DATE;",
    },
    {
        "input": "What LSU events are happening today?",
        "query": "SELECT * FROM public.events WHERE DATE(start_date) = CURRENT_DATE;",
    },
    {
        "input": "Any events happening tonight at union?",
        "query": "SELECT * FROM public.events WHERE DATE(start_date) = CURRENT_DATE;",
    },
    {
        "input": "Any interesting events happening today or tomorrow?",
        "query": """
            SELECT * FROM public.events 
            WHERE DATE(start_date) = CURRENT_DATE 
            OR DATE(start_date) = CURRENT_DATE + INTERVAL '1 day';
        """,
    },
    {
        "input": "Show me events happening tomorrow.",
        "query": "SELECT * FROM public.events WHERE DATE(start_date) = CURRENT_DATE + INTERVAL '1 day';",
    },
    {
        "input": "Show me events happening at the union tomorrow.",
        "query": "SELECT * FROM public.events WHERE DATE(start_date) = CURRENT_DATE + INTERVAL '1 day';",
    },
    {
        "input": "List all events scheduled for this week.",
        "query": """
            SELECT * FROM public.events 
            WHERE DATE(start_date) >= DATE_TRUNC('week', CURRENT_DATE) 
            AND DATE(start_date) < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week';
        """,
    },
    {
        "input": "Find events occurring next week.",
        "query": """
            SELECT * FROM public.events 
            WHERE DATE(start_date) >= DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '1 week' 
            AND DATE(start_date) < DATE_TRUNC('week', CURRENT_DATE) + INTERVAL '2 weeks';
        """,
    },
]


class SQLQueryAgent:
    def __init__(self, llm=None, embeddings=None, supabase=None):
        self.supabase = supabase if supabase else create_supabase_client()
        self.embeddings = embeddings if embeddings else OpenAIEmbeddings()
        self.llm = (
            llm if llm else ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        )
        self.db = SQLDatabase.from_uri(
            POSTGRES_URI, include_tables=QUERY_TABLES
        )
        self.tools = [
            EventEmbeddingTool(
                embeddings=self.embeddings, supabase=self.supabase
            ),
            SocietyEmbeddingTool(
                embeddings=self.embeddings, supabase=self.supabase
            ),
        ]

        self.example_selector = None
        self.few_shot_prompt = None
        self.full_prompt = None
        self.agent = None

    async def initialise(self):
        self.example_selector = (
            await SemanticSimilarityExampleSelector.afrom_examples(
                EXAMPLES,
                self.embeddings,
                FAISS,
                k=3,
                input_keys=["input"],
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
            extra_tools=self.tools,
            prompt=self.full_prompt,
            agent_type="openai-tools",
            verbose=False,
        )

    async def process(self, message: str):
        response = await self.agent.ainvoke({"input": message})
        return response["output"]
