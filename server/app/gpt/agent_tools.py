from langchain.tools import BaseTool
from langchain.pydantic_v1 import Extra

class SocietyEmbeddingTool(BaseTool):
    name = "SocietyEmbeddingTool"
    description = """
        Use this tool to look up society name values to filter on. 
        If you want to query by society name use this tool to perform a semantic search to 
        retrieive the most relevant societies names and associated data on these societies.
        The input is an approximate spelling of the proper noun.
        Output is a list of the most relevant societies based on the input.
    """
    class Config:
        extra = Extra.allow
        
    def __init__(self, supabase, embeddings):
        super().__init__(supabase=supabase, embeddings=embeddings)
        self.supabase = supabase
        self.embeddings = embeddings
    
    def _run(self, society_name: str):
        k = 5
        embedded_query = self.embeddings.embed_query(society_name)
        response = self.supabase.rpc(
            "match_societies",
            {"query_embedding": embedded_query, "match_count": k},
        ).execute()
        
        ids = [soc['id'] for soc in response.data]
        
        response = self.supabase.table("societies").select('*').in_('id', ids).execute()
        return response.data
    
    def _arun(self):
        raise NotImplementedError("This tool does not support async.")

class EventEmbeddingTool(BaseTool):
    name = "EventEmbeddingTool"
    description = """
        This tool should be used when the user is asking about events and specifically
        event names or information which should be filtered on.
        Specifically, events relating to Loughborough university, 
        the student union, the union, and LSU. Use this tool to look up events to filter on. 
        If you want to query by Event name use this tool to perform a semantic search to 
        retrieive the most relevant societies names and associated data on these societies.
        The input is relevant text to do with the event from the user's query. 
        Output is a list of the most relevant events based on the input.
    """
    class Config:
        extra = Extra.allow
        
    def __init__(self, supabase, embeddings):
        super().__init__(supabase=supabase, embeddings=embeddings)
        self.supabase = supabase
        self.embeddings = embeddings
    
    def _run(self, event_query: str):
        k = 10
        embedded_query = self.embeddings.embed_query(event_query)
        response = self.supabase.rpc(
            "match_events",
            {"query_embedding": embedded_query, "match_count": k},
        ).execute()
        
        ids = [event['id'] for event in response.data]
        
        response = self.supabase.table("events").select('*').in_('id', ids).execute()
        return response.data
    
    def _arun(self):
        raise NotImplementedError("This tool does not support async.")



