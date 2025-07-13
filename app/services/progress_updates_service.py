# app/services/progress_updates_service.py
from datetime import datetime
from app.models import db, Objective, Task, ProgressUpdate, Status, User
from app.utils import check_access_scope


def add_progress(objective_id, data, user):
    objective = Objective.query.get_or_404(objective_id)
    task = Task.query.get_or_404(objective.task_id)

    if not (check_access_scope(user, task.organization_id, 'edit') or user.id == objective.assigned_user_id):
        return {'error': '進捗追加の権限がありません'}, 403

    progress = ProgressUpdate(
        objective_id=objective_id,
        status_id=data['status_id'],
        detail=data['detail'],
        report_date=datetime.strptime(data['report_date'], '%Y-%m-%d'),
        updated_by=user.id
    )
    db.session.add(progress)
    db.session.commit()
    return {'message': '進捗を追加しました'}, 201


def get_progress_list(objective_id, user):
    objective = Objective.query.get_or_404(objective_id)
    task = Task.query.get_or_404(objective.task_id)

    if not check_access_scope(user, task.organization_id, 'view'):
        return {'error': '閲覧権限がありません'}, 403

    progress_list = ProgressUpdate.query.filter_by(objective_id=objective_id, is_deleted=False).all()
    return [
        {
            'id': p.id,
            'status': db.session.get(Status, p.status_id).name,
            'detail': p.detail,
            'report_date': p.report_date.strftime('%Y-%m-%d'),
            'updated_by': db.session.get(User, p.updated_by).name
        } for p in progress_list
    ], 200


def get_latest_progress(objective_id, user):
    objective = Objective.query.get_or_404(objective_id)
    task = Task.query.get_or_404(objective.task_id)

    if not check_access_scope(user, task.organization_id, 'view'):
        return {'error': '閲覧権限がありません'}, 403

    progress = (
        ProgressUpdate.query
        .filter_by(objective_id=objective_id, is_deleted=False)
        .order_by(ProgressUpdate.report_date.desc(), ProgressUpdate.created_at.desc())
        .first()
    )

    if not progress:
        return {
            'status': '-',
            'report_date': '-',
            'detail': '-',
            'updated_by': '-'
        }, 200

    status = db.session.get(Status, progress.status_id)
    user_name = db.session.get(User, progress.updated_by).name

    return {
        'status': status.name if status else '-',
        'report_date': progress.report_date.strftime('%Y-%m-%d'),
        'updated_by': user_name,
        'detail': progress.detail
    }, 200


def delete_progress(progress_id, user):
    progress = ProgressUpdate.query.get_or_404(progress_id)
    objective = Objective.query.get_or_404(progress.objective_id)
    task = Task.query.get_or_404(objective.task_id)

    if not check_access_scope(user, task.organization_id, 'full'):
        return {'error': '削除権限がありません'}, 403

    progress.soft_delete()
    db.session.commit()
    return {'message': '進捗を削除しました'}, 200
