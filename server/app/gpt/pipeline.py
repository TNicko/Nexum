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
from app.utils.time_utils import log_time
from dotenv import load_dotenv
from datetime import date 
from urlextract import URLExtract
load_dotenv()


class GPTPipeline:
    def __init__(self, model_name: str = "gpt-3.5-turbo-0125", streaming: bool = False, supabase = None):
        self.supabase = supabase if supabase else create_supabase_client()
        self.callback = AsyncIteratorCallbackHandler()
        self.llm = ChatOpenAI(temperature=0, model_name=model_name)
        self.stream_llm = ChatOpenAI(temperature=0, model_name=model_name, streaming=streaming, callbacks=[self.callback])
        self.output_parser = StrOutputParser()
        self.embeddings = OpenAIEmbeddings()
        self.sql_agent = SQLQueryAgent(llm=self.llm, embeddings=self.embeddings, supabase=self.supabase)
        self.streaming = streaming

    async def stream_response(self, messages):
        """ Stream responses from the language model. """
        prompt, relevant_urls = await self._process(messages)
        relevant_urls_new =  [f'"{url}"' for url in relevant_urls]
        relevant_urls_new = ', '.join(relevant_urls_new)
        relevant_urls_new = f"[{relevant_urls_new}]"
        #print(prompt)
        print("relevant urls sent:")
        print(relevant_urls_new)
        yield f"data: {relevant_urls_new}\n\n"
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
        todays_date = date.today() 
        prompt = ChatPromptTemplate.from_messages(
            [("system", sp.SIMPLIFY_MSG_PROMPT), ("user", "{input}")]
        )
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
        msg_to_return =  chain.invoke({"input": message})
        return (msg_to_return, urls_found)

    def _beautify(self, message, query):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", sp.BEAUTIFY_PROMPT),
                ("user", f"Question: {query}. Answer: {message}"),
            ]
        )
        return prompt.format()

    async def _process(self, messages):
        simplify_start_time = time.time()
        simplified_request = await self._simplify_message_history(messages)
        log_time("Simplification process", simplify_start_time)
        print(simplified_request)
        
        embed_start_time = time.time()
        embedding_response = await self._get_embedding_response(simplified_request)
        log_time("Embedding response time", embed_start_time)
        print(embedding_response)

        
        sql_start_time = time.time()
        await self.sql_agent.initialise()
        sql_response = await self.sql_agent.process(simplified_request)
        log_time("SQL agent response time", sql_start_time)
        print(sql_response)

        no_url_start_time = time.time()
        no_url_response, relevant_urls = await self._get_url_seperated(sql_response + '\n' + embedding_response)
        log_time("Embedding remove url response time", no_url_start_time)
        print(no_url_response)
        print("Relevant urls:")
        print(relevant_urls)

        final_prompt = self._beautify(
            no_url_response, simplified_request
        )
        return final_prompt, relevant_urls
