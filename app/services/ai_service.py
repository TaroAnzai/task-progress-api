# app/services/ai_service.py

from celery.result import AsyncResult
from app.ai.ai_tasks import run_ai_suggestion
from celery_app import celery

def enqueue_ai_task(data: dict):
    """
    AI提案処理をCeleryにキューイング
    """
    task_info = data.get("task_info")
    mode = data.get("mode", "task_name")

    if not task_info:
        return {"error": "task_info が指定されていません"}, 400

    if mode not in ("task_name", "objectives"):
        return {"error": f"無効な mode: {mode}"}, 400

    result = run_ai_suggestion.delay(task_info, mode)
    return {"job_id": result.id}, 202


def get_ai_task_result(job_id: str):
    """
    Celeryで実行中のAI提案処理の結果を取得
    """
    result = AsyncResult(job_id, app=celery)

    if result.state == "PENDING":
        return {"status": "processing"}, 202
    elif result.state == "FAILURE":
        return {"status": "error", "message": str(result.result)}, 500
    elif result.state == "SUCCESS":
        data = result.result
        data["job_id"] = job_id
        return data, 200
    else:
        return {"status": result.state}, 202
