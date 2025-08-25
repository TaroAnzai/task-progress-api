# celery_app.py
from celery import Celery
import os
from dotenv import load_dotenv
from celery.schedules import crontab

if os.getenv("PYTEST_CURRENT_TEST"):
    # ✅ pytest実行中ならテスト用.envを読み込む
    env_file = ".env.test"
else:
    env_file = ".env"

load_dotenv(env_file, override=True)

celery = Celery(
    __name__,
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

celery.conf.update(
    timezone="Asia/Tokyo",
    task_routes={
        "app.tasks.notifications.*": {"queue": "mail"},
        "app.tasks.ai.*":            {"queue": "ai"},
    },
    beat_schedule={
        "daily-progress-reminder-09": {
            "task": "app.tasks.notifications.daily_progress_reminder",
            "schedule": crontab(minute=0, hour=9),
            "options": {"queue": "mail"},
        },    
    },
    task_ignore_result=False, 
    broker_connection_retry_on_startup=True
)
celery.autodiscover_tasks(["app.tasks"])
