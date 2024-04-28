# from supabase import Client, create_clientfrom 
from supabase_py_async import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_KEY: str = os.getenv("SUPABASE_KEY")


async def create_supabase_client():
    supabase = await create_client(SUPABASE_URL, SUPABASE_KEY)
    return supabase



