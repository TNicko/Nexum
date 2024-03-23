import hashlib
import time
from typing import Dict, List, Any 
from itemadapter import ItemAdapter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from app.db.supabase import create_supabase_client
from app.utils.time_utils import log_time
from app.scrapy_app.scrapy_app.filter import ContentFilter

from app.utils.log_config import setup_colored_logger
logger = setup_colored_logger("pipeline")
logger.propagate = False

DATABASE_TABLE = "documents_test"

class ScrapyAppPipeline:
    def __init__(self):
        self.supabase = create_supabase_client()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            is_separator_regex=False,
        )
        self.embeddings = OpenAIEmbeddings()

    def process_item(self, item, spider):
        start_pipeline_time = time.time()
        adapter = ItemAdapter(item)
        url = adapter.get("url")
        content = adapter.get("content") 
        file_name = adapter.get("file_name")
      
        # Apply the content filter 
        # NOTE: placing this here before checking if URL exists may mean
        # that it will ignore updated versions i.e. older versions of the same
        # url that were valid will not be deleted.
        filter = ContentFilter(content)
        filter.check_min_length(500)

        if not filter.validate():
            logger.debug("Content does not meet the criteria.")
            return item

        # Compute the content hash.
        hash_start_time = time.time()
        content_hash = self.compute_hash(content)
        log_time("Hash computation", hash_start_time)

        # Check if item already exists and if it needs to be updated.
        response = (
            self.supabase.table("documents_test")
            .select("*")
            .eq("url", url)
            .execute()
        )
        page_chunks = response.data
        if not page_chunks:
            logger.debug("Page does not exist yet. Uploading page content...")
            
            documents = self.generate_content_documents(
                content, url, file_name, content_hash
            )
            self.upsert_documents(documents)

        elif (page_chunks[0])["page_hash"] == content_hash:
            logger.debug("Hash is the same. Ignoring...")

        else:
            logger.debug("Hash is different. Updating page content...")

            self.delete_documents(url)

            documents = self.generate_content_documents(
                content, url, file_name, content_hash
            )
            self.upsert_documents(documents)
        
        
        log_time("Total processing time for item", start_pipeline_time)
        return item

    def compute_hash(self, content: str):
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    
    def generate_content_documents(
        self, content: str, url: str, file_path: str, content_hash: str
    ):
        start_time_overall = time.time()

        # Start time for document splitting
        start_time_splitting = time.time()
        chunks = self.text_splitter.create_documents([content])
        log_time("Document splitting", start_time_splitting)

        documents = []
        for i, chunk in enumerate(chunks):
            # Log time for setting metadata for each chunk
            chunk.metadata = {
                "file_path": file_path,
                "chunk": i,
            }

            # Log time for embedding generation for each chunk
            start_time_embedding = time.time()
            embedding = self.embeddings.embed_query(chunk.page_content)
            log_time(f"Embedding generation for chunk {i}", start_time_embedding)

            document = {
                "content": chunk.page_content,
                "embedding": embedding,
                "metadata": chunk.metadata,
                "source": "loughborough-website",
                "url": url,
                "page_hash": content_hash,
            }

            documents.append(document)

        log_time("Total page documents generation", start_time_overall)
        return documents

    def upsert_documents(self, documents: List[Dict[str, Any]]):
        insert_start_time = time.time()
        self.supabase.table(DATABASE_TABLE).insert(documents).execute()
        log_time("Document Insertion", insert_start_time)

    def delete_documents(self, url: str):
        delete_start_time = time.time()
        self.supabase.table(DATABASE_TABLE).delete().eq('url', url).execute()
        log_time("Chunk Deletion", delete_start_time)
