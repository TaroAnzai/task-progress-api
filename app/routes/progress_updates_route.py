# app/routes/progress_updates_route.py
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.services import progress_updates_service

progress_bp = Blueprint('progress_updates', __name__)


@progress_bp.route('/objectives/<int:objective_id>/progress', methods=['POST'])
@login_required
def add_progress(objective_id):
    result, status = progress_updates_service.add_progress(objective_id, request.json, current_user)
    return jsonify(result), status


@progress_bp.route('/objectives/<int:objective_id>/progress', methods=['GET'])
@login_required
def get_progress(objective_id):
    result, status = progress_updates_service.get_progress_list(objective_id, current_user)
    return jsonify(result), status


@progress_bp.route('/objectives/<int:objective_id>/latest-progress', methods=['GET'])
@login_required
def get_latest_progress(objective_id):
    result, status = progress_updates_service.get_latest_progress(objective_id, current_user)
    return jsonify(result), status


@progress_bp.route('/progress/<int:progress_id>', methods=['DELETE'])
@login_required
def delete_progress(progress_id):
    result, status = progress_updates_service.delete_progress(progress_id, current_user)
    return jsonify(result), status
