from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from db.supabase import create_supabase_client
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()


supabase = create_supabase_client()
embeddings = OpenAIEmbeddings()

vstore = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name="documents",
    query_name="match_documents",
)
query = "what is loughborough unis history?"
# k : number of retrieved results
# filter : metadata to filer responses
matched_docs = vstore.similarity_search_with_relevance_scores(
    query=query, k=5, filter=None
)
for doc in matched_docs:
    print(f"{doc}\n")
