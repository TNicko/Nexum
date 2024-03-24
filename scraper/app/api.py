from fastapi import FastAPI
from app.celery_app.tasks.uni_website_task import run_scrapy_spider
from app.celery_app.tasks.events_task import fetch_and_store_events 
from app.celery_app.tasks.societies_task import fetch_and_store_societies
app = FastAPI()

@app.post("/run-spider")
async def run_spider():
    run_scrapy_spider.delay()
    return {"message": "Spider is running..."}

@app.post("/run-events")
async def run_events():
    fetch_and_store_events.delay()
    return {"message": "Extracting & Storing Events..."} 

@app.post("/run-societies")
async def run_events():
    fetch_and_store_societies.delay()
    return {"message": "Extracting & Storing Societes..."} 
