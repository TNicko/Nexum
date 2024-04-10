import logging
from app.celery_app import celery_app
from celery.utils.log import  get_task_logger

logger = get_task_logger(__name__)
logger.setLevel(logging.INFO)

@celery_app.task(name="test")
def test_task():
    logger.info(f"Test task has run!")

