from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app.services import task_core_service

task_core_bp = Blueprint('task_core', __name__, url_prefix='/tasks')

@task_core_bp.route('', methods=['POST'])
@login_required
def create_task():
    return task_core_service.create_task(request.json, current_user)

@task_core_bp.route('/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    return task_core_service.update_task(task_id, request.json, current_user)

@task_core_bp.route('/<int:task_id>', methods=['DELETE'])
@login_required
def delete_task(task_id):
    return task_core_service.delete_task(task_id, current_user)

@task_core_bp.route('', methods=['GET'])
@login_required
def get_tasks():
    return task_core_service.get_tasks(current_user)

@task_core_bp.route('/<int:task_id>/objectives/order', methods=['POST'])
@login_required
def update_objective_order(task_id):
    return task_core_service.update_objective_order(task_id, request.json)
