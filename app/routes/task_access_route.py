from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app.services import task_access_service

task_access_bp = Blueprint('task_access', __name__, url_prefix='/tasks/<int:task_id>/scope')

@task_access_bp.route('/access_levels', methods=['PUT'])
@login_required
def update_access_level(task_id):
    return task_access_service.update_access_level(task_id, request.json, current_user)

@task_access_bp.route('/users', methods=['GET'])
@login_required
def get_task_users(task_id):
    return task_access_service.get_task_users(task_id)

@task_access_bp.route('/access_users', methods=['GET'])
@login_required
def get_task_access_users(task_id):
    return task_access_service.get_task_access_users(task_id)

@task_access_bp.route('/access_organizations', methods=['GET'])
@login_required
def get_task_access_organizations(task_id):
    return task_access_service.get_task_access_organizations(task_id)
