from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services import task_order_service

task_order_bp = Blueprint('task_order', __name__, url_prefix='/task_order')

@task_order_bp.route('/<int:user_id>', methods=['GET'])
@login_required
def get_task_order(user_id):
    return task_order_service.get_task_order(user_id)

@task_order_bp.route('/<int:user_id>', methods=['POST'])
@login_required
def save_task_order(user_id):
    return task_order_service.save_task_order(user_id, request.json)
