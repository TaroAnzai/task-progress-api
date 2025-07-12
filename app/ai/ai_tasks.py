# progress/ai/ai_tasks.py
from celery_app import celery
from app.ai.gemini_client import GeminiAISuggestionClient

@celery.task(bind=True)
def run_ai_suggestion(self, task_info: dict, mode: str = "task_name") -> dict:
    print(f"[AI_TASK] Received task_info: {task_info} (type: {type(task_info)}), mode: {mode}")
    
    try:
        if not isinstance(task_info, dict):
            raise ValueError(f"task_info must be dict, got {type(task_info)}")

        client = GeminiAISuggestionClient()

        if mode == "task_name":
            result = client.suggest_task_name(task_info)
            print(f"[AI_TASK DEBUG] result from suggest_task_name: {result} (type={type(result)})")
        elif mode == "objectives":
            result = client.generate_objectives(task_info)
        else:
            raise ValueError(f"Invalid mode: {mode}")

        return {
            "status": "success",
            "mode": mode,
            "result": result
            }

    except Exception as e:
        print(f"[AI_TASK ERROR] {e}")
        return {"status": "error", "message": str(e)}