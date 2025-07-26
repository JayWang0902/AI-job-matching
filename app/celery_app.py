from celery import Celery
from celery.schedules import crontab
from dotenv import load_dotenv

load_dotenv()

from app.core.config import settings

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks"]
)

celery_app.conf.update(
    task_track_started=True,
)

# Celery Beat Schedule
# This will run the run_daily_flow task every day at 4:00 AM
celery_app.conf.beat_schedule = {
    'run-daily-matching-flow': {
        'task': 'app.tasks.run_daily_flow',
        'schedule': crontab(hour=4, minute=0),
    },
}
