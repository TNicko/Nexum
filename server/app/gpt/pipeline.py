from app.gpt.sql_query import getNonVectorizedData  
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts.chat import ChatPromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

def getVectorizedDataV2(supabase, queryToMatch):
    embeddings_model = OpenAIEmbeddings()
    embedded_query = embeddings_model.embed_query(queryToMatch)

    k=10
    # filter=None
    # threshold = 0

    response = supabase.rpc('match_documents', {'query_embedding': embedded_query, 'match_count': k}).execute()

    documentString = ""
    for doc in response.data:
        documentString = documentString + "Website chunk "+ (doc["url"])+" --- " + (doc["content"]) + " --- "


    llm = ChatOpenAI(openai_api_key="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", temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        #("system", "You are a bot designed to parse information from several chunks of text from websites, giving an answer to a given question or statement. You must only use information from the chunks themselves and not come up with any information on your own. If the answer isn't found within the chunks, reply with 'Sorry, this is outside the scope of my information' rather than making up an answer."),
        ("system", "Parse information from several chunks of text from websites to answer a question or statement. Only use information from the chunks themselves and not come up with any information on your own. If the answer isn't found within the chunks, reply with '---' rather than making up an answer. Make sure to include all relevant information as well as the urls of the chunks which provided the key information."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": "Question: "+queryToMatch+" Information: "+documentString}))

def simplifyMessageHistory(messageHistory):
    messageHistory = "---".join(messageHistory)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        #("system", "You are a bot designed to take a series of in order messages, seperated by ---, between a student and a chatbot and return a simplified question based on the most recent message. If the last message relates to previous messages sent, you should take that into account when forming the simplified request. You must only use information from the messages themselves and not come up with any information on your own."),
        ("system", "Based on this series of messages between a user and a chatbot, what is the latest thing the user is asking? Only say the answer and nothing else."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": messageHistory}))

def generateMYSQLReq(toMakeSQL):
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot designed to write a mysql request based on an question or statement for the 'events' table on the 'websites' database."),
        ("user", "{input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": toMakeSQL}))

def beautify(messageToSimplify, question):
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")
    output_parser = StrOutputParser()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a bot designed to format a given answer to a question into a more readable form. Make sure to include all relevant information, including urls under 'sources'. If there is duplicate information, you should remove it. If the answer refers to not knowing the answer but also gives an answer, remove the part about not knowing the answer. You must only use information from the messages themselves and not come up with any information on your own."),
        ("user", "Question: {question}. Answer: {input}")
    ])
    chain = prompt | llm | output_parser

    return(chain.invoke({"input": messageToSimplify, "question": question}))


def gptPipeline(supabase, messages):
    simplifiedRequest = simplifyMessageHistory(messages)
    vectorizedReturn = getVectorizedDataV2(supabase, simplifiedRequest)
    nonVectorizedReturn = getNonVectorizedData(simplifiedRequest)
    responseToUser = beautify(vectorizedReturn + nonVectorizedReturn, simplifiedRequest)
    return responseToUser
