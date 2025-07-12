# celery_app.py
from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()  # .envファイルの読み込み

celery = Celery(
    "progress_ai_tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    broker_connection_retry_on_startup=True
)

celery.conf.update(
    broker_connection_retry_on_startup=True
)

import app.ai.ai_tasks