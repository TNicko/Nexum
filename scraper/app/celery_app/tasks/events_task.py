from langchain_openai import OpenAIEmbeddings
import requests
import logging
from celery.utils.log import get_task_logger
from app.celery_app import celery_app
from app.db.supabase import create_supabase_client


logger = get_task_logger("events_task")
logger.setLevel(logging.INFO)



def create_event_description(event):
    """Generates a descriptive string for an event for embedding."""
    return (
        f"{event['name']} {event['subtitle']}"
        f"{event['description']} {event['type']} "
        f"from {event['start_date']} to {event['end_date']}"
    )


@celery_app.task(name="events")
def fetch_and_store_events():
    logger.info(f"Fetching and storing events...")
    
    supabase = create_supabase_client()
    url = "https://pluto.sums.su/api/events?perPage=200&sortBy=start_date&futureOrOngoing=1"
    headers = {"X-Site-Id": "dEJdtTysQf53J7AMAD9zde"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"HTTP error {response.status_code} fetching events")
            return

        events = response.json().get("data", [])
        if not events:
            logger.info(f"Completed: No new events to store")
            return

        logger.info(f"Found {len(events)} events, starting upsert operations")

        event_data_list = [{
            "id": event.get("id"),
            "name": event.get("title"),
            "subtitle": event.get("event_date_title"),
            "url": f"https://lsu.co.uk/events/id/{event.get('event_id')}-{event.get('url_name')}",
            "description": event.get("short_description"),
            "type": event.get("type", {}).get("name"),
            "start_date": event.get("start_date"),
            "end_date": event.get("end_date"),
        } for event in events]
        

        embeddings = OpenAIEmbeddings()
        event_embeddings_data = [
            {
                "id": event["id"],
                "name": event["name"],
                "embedding": embeddings.embed_query(
                   create_event_description(event) 
                ) 
            }
            for event in event_data_list
        ]

        # Upsert to insert or update based on the id field
        supabase.table("events").upsert(event_data_list, on_conflict="id").execute()
        supabase.table("event_embeddings").upsert(event_embeddings_data, on_conflict="id").execute()
        logger.info("Successfully upserted events data.")
    
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

