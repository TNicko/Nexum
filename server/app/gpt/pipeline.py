from app.gpt.sql_query import SQLQueryAgent
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from app.db.supabase import create_supabase_client
import app.gpt.system_prompts as sp
from dotenv import load_dotenv

load_dotenv()


class GPTPipeline:
    def __init__(self, model_name: str = "gpt-3.5-turbo-0125"):
        self.supabase = create_supabase_client()
        self.llm = ChatOpenAI(temperature=0, model_name=model_name)
        self.output_parser = StrOutputParser()
        self.embeddings = OpenAIEmbeddings()
        self.sql_agent = SQLQueryAgent(llm=self.llm, embeddings=self.embeddings) 

    def _get_embedding_response(self, queryToMatch, k: int = 10):
        embedded_query = self.embeddings.embed_query(queryToMatch)
        response = self.supabase.rpc(
            "match_documents",
            {"query_embedding": embedded_query, "match_count": k},
        ).execute()
        document_string = " ".join(
            f"Website chunk {doc['url']} --- {doc['content']}"
            for doc in response.data
        )

        prompt = ChatPromptTemplate.from_messages(
            [("system", sp.EMBEDDING_RSP_PROMPT), ("user", "{input}")]
        )
        chain = prompt | self.llm | self.output_parser

        return chain.invoke(
            {
                "input": "Question: "
                + queryToMatch
                + " Information: "
                + document_string
            }
        )

    def _simplify_message_history(self, messages):
        message_history = "---".join(messages)
        prompt = ChatPromptTemplate.from_messages(
            [("system", sp.SIMPLIFY_MSG_PROMPT), ("user", "{input}")]
        )
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"input": message_history})

    def _beautify(self, message, query):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", sp.BEAUTIFY_PROMPT),
                ("user", "Question: {query}. Answer: {input}"),
            ]
        )
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"input": message, "query": query})

    def process(self, messages):
        simplified_request = self._simplify_message_history(messages)
        embedding_response = self._get_embedding_response(simplified_request)
        sql_response = self.sql_agent.process(simplified_request)
        merged_response = self._beautify(
            embedding_response + sql_response, simplified_request
        )
        return merged_response
