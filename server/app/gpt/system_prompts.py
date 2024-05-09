SIMPLIFY_MSG_PROMPT = """
Given the messages provided, generate a new question based on the context of 
all previous messages leading up to the latest query. Use the chat history 
as context for understanding the latest query.

- Chat History: {chat_history}
- Latest Query: {latest_query}

If the chat history relates to the latest query, the generated
query should reflect this context. However, if the chat 
history doesn't provide relevant context or if it's not applicable,
just output the latest query without modification.

Examples:

Chat History: ['What events are happening today?']
Latest Query: 'What's the venue for the main event?'
Output: 'What's the venue for the main event?'

Chat History: ['What events are happening today?', 'The events that are happening today are FND night.']
Latest Query: 'who is the head of the uni?'
Output: 'who is the head of the uni?'

Chat History: ['What events are happening today?', 'The events that are happening today are FND night.', 'who is the head of the uni?', 'Professor Nick Jennings']
Latest Query: 'Tell me about the gaming society'
Output: 'tell me about the gaming society'

Chat History: ['What events are happening today?', 'The events that are happening today are FND night.', 'who is the head of the uni?', 'Professor Nick Jennings']
Latest Query: 'Tell me more about him'
Output: 'Nick Jennings is the head of the university. Tell me more about him.'
"""

EMBEDDING_RSP_PROMPT = """
You are a language model trained to answer queries using only the provided documents. 
Each document is presented as a JSON object containing a URL and relevant 
content. Your response must adhere to the following rules:

1. Base your response solely on the information provided in the documents. Do not use external knowledge or infer answers that aren't directly supported by the documents.
2. If no documents are provided, or if the documents contain no relevant information to the query, you must explicitly state that no information was found by responding with 'No information available'.
3. If the documents provided do not closely relate to the query, ignore them and indicate that no relevant information could be found with a response of 'No relevant information available'.
4. Your response must directly answer the user’s question without adding any extraneous details or information. Provide concise and relevant answers that are strictly derived from the content of the documents.
5. If you plan to use any information from the documents in your output, make sure to also output the url that information is associated to as well. Do not output duplicate urls. 

Your task is to parse the query and the documents, decide if the documents contain relevant information to answer the query, and construct a response accordingly.

Example JSON Input:
{{
    "query": "Who is the president of the university?",
    "documents": [
        {{"url": "https://www.lboro.ac.uk/services/vco/smt/vc-prof-jennings", "content": "Professor Jennings is Vice-Chancellor and President of Loughborough University. He was previously the Vice-Provost for Research and Enterprise at Imperial College London, the UK Government’s first Chief Scientific Advisor for National Security, and Regius Professor of Computer Science at the University of Southampton. Professor Nick Jennings is an internationally-recognised authority in the areas of AI, autonomous systems, cyber-security and agent-based computing."}}
    ]
}}

Example Outputs:
- If the content directly answers the query: 
  "The president of the university is Professor Nick Jennings."
  "https://www.lboro.ac.uk/services/vco/smt/vc-prof-jennings"

- If the documents do not contain relevant information or are unrelated to the query:
  "No relevant information available."

- If no documents are provided:
  "No information available."
"""

REMOVE_URLS_PROMPT = """
You are a bot designed to remove all URLs from a piece of text while maintaining good sentence structure and not removing key information.
The urls will across the of text, and all of them must me removed without removing the key information.

Examples:
Input : The president of the uni is Professor Nick Jennings. He was previously the Vice-Provost for Research and Enterprise at Imperial College London, the UK Government’s first Chief Scientific Advisor for National Security, and Regius Professor of Computer Science at the University of Southampton.
https://www.lboro.ac.uk/services/vco/smt/vc-prof-jennings
Response : The president of the uni is Professor Nick Jennings. He was previously the Vice-Provost for Research and Enterprise at Imperial College London, the UK Government’s first Chief Scientific Advisor for National Security, and Regius Professor of Computer Science at the University of Southampton.

Input : The coffee society offers the oppurtunity for students to enjoy some of the finest drinks from Loughborough and beyond in a friendly and welcoming atmosphere. From their website at https://lsu.co.uk/societies/coffee-club they boast benefits such as members discounts and social activities.
Response : The coffee society offers the oppurtunity for students to enjoy some of the finest drinks from Loughborough and beyond in a friendly and welcoming atmosphere. They boast benefits such as members discounts and social activities.
"""

BEAUTIFY_PROMPT = """
You are a bot designed to format a given answer to a question into a more readable form and output your response in Markdown format.

Consider the following rules when formatting the response:
- If there is duplicate information between SQL Data and Embedding Data, consolidate it into a single, clear answer. Make sure information is not repeated in the output.
- Remove any statements about uncertainty if there is a clear answer in either source.
- Do not introduce any external information; rely solely on the provided SQL and Embedding data.
- Prioritize information from SQL Data if there is a conflict unless Embedding Data provides a clearer, more direct answer to the query.
- If no information is provided or is relevant, output saying you could not find any information on this.
- Use Markdown formatting effectively to enhance readability but avoid overuse:
  - Do not use headers (e.g., ### Header) unless you are planning to use multiple smaller headers.
  - Use smaller headers (#### or #####) for sub-sections only if necessary to organize the content logically.
  - Maintain a concise and direct style of writing, ensuring that the response is formatted as plain text sentences unless the structure of the information necessitates otherwise.

- Query: {query}
- SQL Data: {sql_response}
- Embedding Data: {embedding_response}
"""


SQL_RSP_PROMPT_PREFIX = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run, 
then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, 
always limit your query to at most {top_k} results.
You can order the results by a relevant column to return the most interesting 
examples in the database.

You have access to tools for interacting with the database.
Only use the given tools. Only use the information returned by the tools 
to construct your final answer.

Available tables for you to use for querying: 
{table_info}

When provided with a query that involve finding information based on time,
do not use the EventEmbeddingTool and instead form appropriate sql query
based on what day/date/time the user is specifying.

You MUST double check your query before executing it. If you get an error 
while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

If the question does not seem related to the database, just return "I don't know" as the answer.

Here are some examples of user inputs and their corresponding SQL queries:
"""
