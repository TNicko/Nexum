import json
import logging
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
from app.utils.log_config import setup_colored_logger
from app.utils.time_utils import log_time
from dotenv import load_dotenv
from datetime import date
from urlextract import URLExtract

load_dotenv()

logger = setup_colored_logger("pipeline")
logger.propagate = False
logger.level = logging.DEBUG


class GPTPipeline:
    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo-0125",
        streaming: bool = False,
        supabase=None,
    ):
        logger.info(
            "Initializing GPTPipeline with model_name=%s, streaming=%s",
            model_name,
            streaming,
        )
        self.supabase = supabase if supabase else create_supabase_client()
        self.callback = AsyncIteratorCallbackHandler()
        self.llm = ChatOpenAI(temperature=0, model_name=model_name)
        self.stream_llm = ChatOpenAI(
            temperature=0,
            model_name=model_name,
            streaming=streaming,
            callbacks=[self.callback],
        )
        self.output_parser = StrOutputParser()
        self.embeddings = OpenAIEmbeddings()
        self.sql_agent = SQLQueryAgent(
            llm=self.llm, embeddings=self.embeddings, supabase=self.supabase
        )
        self.streaming = streaming

    async def stream_response(self, messages):
        """Stream responses from the language model."""
        prompt, relevant_urls = await self._process(messages)
        logger.debug(f"Relevant URLS processed: {relevant_urls}")
        # Stream the URLs as first streamed token
        first_message = json.dumps({"type": "urls", "data": relevant_urls})
        yield f"data: {first_message}\n\n"

        model = self.stream_llm

        async def wrap_done(fn: Awaitable, event: asyncio.Event):
            try:
                await fn
            except Exception as e:
                logger.error(f"Caught exception in wrap_done: {e}")
            finally:
                event.set()

        task = asyncio.create_task(
            wrap_done(
                model.agenerate(messages=[[HumanMessage(content=prompt)]]),
                self.callback.done,
            ),
        )

        logger.info("Streaming process started...")
        async for token in self.callback.aiter():
            json_token = json.dumps({"type": "token", "data": token})
            logger.debug(token)
            yield f"data: {json_token}\n\n"

        await task

    async def get_response(self, messages):
        logger.info("Generating response...")
        """ Process the messages and return a single final response. """
        prompt = await self._process(messages)
        try:
            start_time = time.time()
            result = await self.llm.ainvoke(input=prompt)
            log_time("Final output generation", start_time)
            return result
        except Exception as e:
            print(f"Caught exception: {e}")
            return "An error occurred while processing the request."

    async def _get_embedding_response(self, queryToMatch, k: int = 10):
        embedded_query = await self.embeddings.aembed_query(queryToMatch)
        response = await self.supabase.rpc(
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

        return await chain.ainvoke(
            {
                "input": "Question: "
                + queryToMatch
                + " Information: "
                + document_string
            }
        )

    async def _simplify_message_history(self, messages):
        # todays_date = date.today()

        chat_history = messages[:-1]
        latest_query = messages[-1]

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    sp.SIMPLIFY_MSG_PROMPT.format(
                        chat_history=chat_history, latest_query=latest_query
                    ),
                ),
                ("user", "{input}"),
            ]
        )
        logger.debug(f"Simplication prompt:\n{prompt}")
        chain = prompt | self.llm | self.output_parser
        return await chain.ainvoke({"input": messages})

    async def _get_url_seperated(self, message):
        urlextractor = URLExtract()
        urls_found = urlextractor.find_urls(message)
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", sp.REMOVE_URLS_PROMPT),
                ("user", "{input}"),
            ]
        )
        chain = prompt | self.llm | self.output_parser
        msg_to_return = chain.invoke({"input": message})
        return (msg_to_return, urls_found)

    async def _beautify(self, message, query):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", sp.BEAUTIFY_PROMPT),
                ("user", f"Question: {query}. Answer: {message}"),
            ]
        )
        return prompt.format()

    async def _process(self, messages):
        simplify_start_time = time.time()
        simplified_query = await self._simplify_message_history(messages)
        logger.debug(f"Simplified query: {simplified_query}")
        log_time("Simplification process", simplify_start_time)

        embed_start_time = time.time()
        embedding_response = await self._get_embedding_response(
            simplified_query
        )
        logger.debug(f"Embedding response:\n{embedding_response}")
        log_time("Embedding response time", embed_start_time)

        embed_no_url_start_time = time.time()
        no_url_embedding_response, embed_relevant_urls = (
            await self._get_url_seperated(embedding_response)
        )
        log_time("Embedding remove url response time", embed_no_url_start_time)

        sql_start_time = time.time()
        await self.sql_agent.initialise()
        sql_response = await self.sql_agent.process(simplified_query)
        log_time("SQL agent response time", sql_start_time)

        urlextractor = URLExtract()
        sql_relevant_urls = urlextractor.find_urls(sql_response)

        final_prompt = await self._beautify(
            sql_response + "\n" + no_url_embedding_response, simplified_query
        )
        return final_prompt, sql_relevant_urls + embed_relevant_urls
