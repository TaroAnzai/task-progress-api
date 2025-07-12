# app/routes/objectives_route.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services import objectives_service

objectives_bp = Blueprint('objectives', __name__)

@objectives_bp.route('/objectives', methods=['POST'])
@login_required
def create_objective():
    result, status = objectives_service.create_objective(request.json, current_user)
    return jsonify(result), status


@objectives_bp.route('/objectives/<int:objective_id>', methods=['PUT'])
@login_required
def update_objective(objective_id):
    result, status = objectives_service.update_objective(objective_id, request.json, current_user)
    return jsonify(result), status


@objectives_bp.route('/tasks/<int:task_id>/objectives', methods=['GET'])
@login_required
def get_objectives_for_task(task_id):
    result, status = objectives_service.get_objectives_for_task(task_id, current_user)
    return jsonify(result), status


@objectives_bp.route('/objectives/<int:objective_id>', methods=['GET'])
@login_required
def get_objective(objective_id):
    result, status = objectives_service.get_objective(objective_id, current_user)
    return jsonify(result), status


@objectives_bp.route('/objectives/<int:objective_id>', methods=['DELETE'])
@login_required
def delete_objective(objective_id):
    result, status = objectives_service.delete_objective(objective_id, current_user)
    return jsonify(result), status


@objectives_bp.route('/statuses', methods=['GET'])
def get_statuses():
    result = objectives_service.get_statuses()
    return jsonify(result)
