# --- task_export_route.py ---

from flask import Blueprint, send_file, jsonify
from flask_login import login_required, current_user
from app.services.task_export_service import TaskDataExporter
from app.models import db

task_export_bp = Blueprint('task_export', __name__)

@task_export_bp.route('/export/excel', methods=['GET'])
@login_required
def export_tasks_excel():
    exporter = TaskDataExporter(current_user.id, db)
    file = exporter.export_as_excel()
    return send_file(file, as_attachment=True, download_name="tasks.xlsx", mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

@task_export_bp.route('/export/yaml', methods=['GET'])
@login_required
def export_tasks_yaml():
    exporter = TaskDataExporter(current_user.id, db)
    yaml_data = exporter.export_as_yaml()
    return jsonify({"yaml": yaml_data})
