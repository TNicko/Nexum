from fastapi import FastAPI
from app.db.supabase import create_supabase_client
from app.celery_app.config import run_scrapy_spider
app = FastAPI()

supabase = create_supabase_client()


@app.post("/run-spider")
async def run_spider():
    run_scrapy_spider.delay()
    return {"message": "Spider is running..."}




