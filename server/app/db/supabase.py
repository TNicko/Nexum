from supabase import Client, create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")


def create_supabase_client():
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase
