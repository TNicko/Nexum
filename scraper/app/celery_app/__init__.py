import os
from celery import Celery
from dotenv import load_dotenv
from celery.app.log import TaskFormatter
from celery.signals import after_setup_task_logger

load_dotenv()

TASKS = [
    "app.celery_app.tasks.events_task.py",
    "app.celery_app.tasks.societies_task.py",
    "app.celery_app.tasks.uni_website_task.py",
]


def make_celery():
    REDIS_URL = os.getenv(
        "CELERY_BROKER_REDIS_URL", "redis://localhost:6379/0"
    )
    celery_app = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

    celery_app.autodiscover_tasks(packages=TASKS)
    return celery_app


celery_app = make_celery()


@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter(
                "%(asctime)s - %(task_id)s - %(task_name)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
