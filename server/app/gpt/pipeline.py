from app.gpt.sql_query import getNonVectorizedData  
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from app.db.supabase import create_supabase_client
from dotenv import load_dotenv

load_dotenv()


class GPTPipeline:
    def __init__(self, model_name: str = "gpt-3.5-turbo-0125"):
        self.supabase = create_supabase_client()
        self.llm = ChatOpenAI(temperature=0, model_name=model_name)
        self.output_parser = StrOutputParser()
        self.embeddings = OpenAIEmbeddings()


    def _get_embedding_response(self, queryToMatch, k: int = 10):
        embedded_query = self.embeddings.embed_query(queryToMatch)
        response = self.supabase.rpc('match_documents', {'query_embedding': embedded_query, 'match_count': k}).execute()
        document_string = " ".join(f"Website chunk {doc['url']} --- {doc['content']}" for doc in response.data)

        prompt = ChatPromptTemplate.from_messages([
            #("system", "You are a bot designed to parse information from several chunks of text from websites, giving an answer to a given question or statement. You must only use information from the chunks themselves and not come up with any information on your own. If the answer isn't found within the chunks, reply with 'Sorry, this is outside the scope of my information' rather than making up an answer."),
            ("system", "Parse information from several chunks of text from websites to answer a question or statement. Only use information from the chunks themselves and not come up with any information on your own. If the answer isn't found within the chunks, reply with '---' rather than making up an answer. Make sure to include all relevant information as well as the urls of the chunks which provided the key information."),
            ("user", "{input}")
        ])
        chain = prompt | self.llm | self.output_parser

        return chain.invoke({"input": "Question: "+queryToMatch+" Information: "+document_string})

    def _simplify_message_history(self, messages):
        message_history = "---".join(messages)
        prompt = ChatPromptTemplate.from_messages([
            #("system", "You are a bot designed to take a series of in order messages, seperated by ---, between a student and a chatbot and return a simplified question based on the most recent message. If the last message relates to previous messages sent, you should take that into account when forming the simplified request. You must only use information from the messages themselves and not come up with any information on your own."),
            ("system", "Based on this series of messages between a user and a chatbot, what is the latest thing the user is asking? Only say the answer and nothing else."),
            ("user", "{input}")
        ])
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"input": message_history})


    def _beautify(self, message, query):
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a bot designed to format a given answer to a question into a more readable form. Make sure to include all relevant information, including urls under 'sources'. If there is duplicate information, you should remove it. If the answer refers to not knowing the answer but also gives an answer, remove the part about not knowing the answer. You must only use information from the messages themselves and not come up with any information on your own."),
            ("user", "Question: {query}. Answer: {input}")
        ])
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"input": message, "query": query})

    
    def process(self, messages):
        simplified_request = self._simplify_message_history(messages)
        embedding_response = self._get_embedding_response(simplified_request)
        sql_response = getNonVectorizedData(simplified_request)
        merged_response = self._beautify(embedding_response + sql_response, simplified_request)
        return merged_response 
