# app/routes/ai_route.py

from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services import ai_service

ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

@ai_bp.route("/suggest", methods=["POST"])
@login_required
def suggest_ai_content():
    """
    タスク情報を受け取り、Geminiによる非同期AI提案を実行する
    mode: "task_name" または "objectives"
    """
    data = request.get_json()
    result, status = ai_service.enqueue_ai_task(data)
    return jsonify(result), status


@ai_bp.route("/result/<job_id>", methods=["GET"])
@login_required
def get_ai_result(job_id):
    """
    指定されたjob_idの非同期AI処理結果を返す
    """
    result, status = ai_service.get_ai_task_result(job_id)
    return jsonify(result), status
