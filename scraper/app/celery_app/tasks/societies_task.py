import requests
import logging
from celery.utils.log import get_task_logger
from app.celery_app import celery_app
from app.db.supabase import create_supabase_client


logger = get_task_logger("societes_task")
logger.setLevel(logging.INFO)


@celery_app.task(name="societies")
def fetch_and_store_societies():
    logger.info(f"Fetching and storing societies...")

    supabase = create_supabase_client()
    SOCIETY_BASE_URL = "https://lsu.co.uk/societies/"
    categories_url = "https://pluto.sums.su/api/groups/categories"
    url = "https://pluto.sums.su/api/groups?sortBy=name&perPage=200&parentCategoryId=1"
    headers = {"X-Site-Id": "dEJdtTysQf53J7AMAD9zde"}
    try:
        categories_response = requests.get(categories_url, headers=headers)
        categories_response.raise_for_status()
        categories = {
            cat["id"]: cat["name"]
            for cat in categories_response.json()
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        societies = response.json()["data"]

        societies_data = [
            {
                "id": society["id"],
                "name": society["name"],
                "url": f"{SOCIETY_BASE_URL}{society['url_name']}",
                "category": categories.get(society["activity_category_id"]),
            }
            for society in societies
        ]

        if societies_data:
            supabase.table("societies").upsert(
                societies_data, on_conflict="id"
            ).execute()
            logger.info("Successfully upserted societies data.")

        else:
            logger.info("No societies data to upsert.")

    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
