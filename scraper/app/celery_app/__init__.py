import os
from celery import Celery
from dotenv import load_dotenv
from celery.app.log import TaskFormatter
from celery.signals import after_setup_task_logger
from celery.schedules import crontab

load_dotenv()

TASKS = [
    "app.celery_app.tasks.test_task",
    "app.celery_app.tasks.events_task",
    "app.celery_app.tasks.societies_task",
    "app.celery_app.tasks.uni_website_task",
]

def make_celery():
    REDIS_URL = os.getenv(
        "CELERY_BROKER_REDIS_URL", "redis://localhost:6379/0"
    )
    celery_app = Celery(__name__, broker=REDIS_URL, backend=REDIS_URL)

    celery_app.autodiscover_tasks(packages=TASKS)
    return celery_app


celery_app = make_celery()

# Scheduler
celery_app.conf.beat_schedule = {
    'test-task': {
        "task": "test",
        "schedule": 5
    },
    'events-task': {
        "task": "events",
        "schedule": crontab(hour=6)
    },
    'societies-task': {
        "task": "societies",
        "schedule": crontab(day_of_week=0)
    },
    # 'uni-website-task': {
        # "task": "uni-website",
        # "schedule": crontab(day_of_month=1),
    # }
}

# Logger
@after_setup_task_logger.connect
def setup_task_logger(logger, *args, **kwargs):
    for handler in logger.handlers:
        handler.setFormatter(
            TaskFormatter(
                "%(asctime)s - %(task_id)s - %(task_name)s - %(levelname)s - %(message)s"
            )
        )
