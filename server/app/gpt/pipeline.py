import asyncio
import time
from typing import Any, Awaitable
from app.gpt.sql_agent import SQLQueryAgent
from langchain.schema import HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.callbacks import AsyncIteratorCallbackHandler
from app.db.supabase import create_supabase_client
import app.gpt.system_prompts as sp
from dotenv import load_dotenv
load_dotenv()


class GPTPipeline:
    def __init__(self, model_name: str = "gpt-3.5-turbo-0125", streaming: bool = False):
        self.supabase = create_supabase_client()
        self.callback = AsyncIteratorCallbackHandler()
        self.llm = ChatOpenAI(temperature=0, model_name=model_name)
        self.stream_llm = ChatOpenAI(temperature=0, model_name=model_name, streaming=streaming, callbacks=[self.callback])
        self.output_parser = StrOutputParser()
        self.embeddings = OpenAIEmbeddings()
        self.sql_agent = SQLQueryAgent(llm=self.llm, embeddings=self.embeddings, supabase=self.supabase)
        self.streaming = streaming

    async def stream_response(self, messages):
        """ Stream responses from the language model. """
        prompt = await self._process(messages)
        model = self.stream_llm
        async def wrap_done(fn: Awaitable, event: asyncio.Event):
            try:
                await fn
            except Exception as e:
                print(f"Caught exception: {e}")
            finally:
                event.set()

        task = asyncio.create_task(wrap_done(
            model.agenerate(messages=[[HumanMessage(content=prompt)]]),
            self.callback.done),
        )

        async for token in self.callback.aiter():
            print("Yielding token: ", token)
            yield f"data: {token}\n\n"

        await task

    async def get_response(self, messages):
        """ Process the messages and return a single final response. """
        prompt = await self._process(messages)
        model = self.llm
        try:
            result = await model.invoke(messages=[[HumanMessage(content=prompt)]])
            return result['choices'][0]['text']  
        except Exception as e:
            print(f"Caught exception: {e}")
            return "An error occurred while processing the request."


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
                ("user", f"Question: {query}. Answer: {message}"),
            ]
        )
        return prompt.format()

    async def _process(self, messages):
        simplified_request = self._simplify_message_history(messages)
        embedding_response = self._get_embedding_response(simplified_request)
        sql_response = self.sql_agent.process(simplified_request)

        final_prompt = self._beautify(
            embedding_response + sql_response, simplified_request
        )
        return final_prompt