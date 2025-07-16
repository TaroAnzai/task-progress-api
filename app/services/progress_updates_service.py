# app/services/progress_updates_service.py
from datetime import datetime
from app.models import db, Objective, Task, ProgressUpdate, Status, User
from app.utils import check_task_access, is_valid_status_id
from app.constants import TaskAccessLevelEnum, StatusEnum, STATUS_LABELS


def get_task_by_id(task_id):
    return Task.query.filter_by(id=task_id, is_deleted=False).first()


def get_task_by_id_with_deleted(task_id):
    return db.session.get(Task, task_id)


def get_objective_by_id(objective_id):
    return Objective.query.filter_by(id=objective_id, is_deleted=False).first()


def get_objective_by_id_with_deleted(objective_id):
    return db.session.get(Objective, objective_id)


def get_progress_by_id(progress_id):
    return ProgressUpdate.query.filter_by(id=progress_id, is_deleted=False).first()


def get_progress_by_id_with_deleted(progress_id):
    return db.session.get(ProgressUpdate, progress_id)


def add_progress(objective_id, data, user):
    objective = get_objective_by_id(objective_id)
    if not objective:
        return {'error': 'オブジェクティブが見つかりません'}, 404
    task = get_task_by_id(objective.task_id)
    if not task:
        return {'error': 'タスクが見つかりません'}, 404

    if not (
        check_task_access(user, task, TaskAccessLevelEnum.EDIT)
        or user.id == objective.assigned_user_id
    ):
        return {'error': '進捗追加の権限がありません'}, 403

    if not is_valid_status_id(data['status_id']):
        return {'error': 'ステータスIDが不正です'}, 400

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
    objective = get_objective_by_id(objective_id)
    if not objective:
        return {'error': 'オブジェクティブが見つかりません'}, 404
    task = get_task_by_id(objective.task_id)
    if not task:
        return {'error': 'タスクが見つかりません'}, 404

    if not check_task_access(user, task, TaskAccessLevelEnum.VIEW):
        return {'error': '閲覧権限がありません'}, 403

    progress_list = ProgressUpdate.query.filter_by(objective_id=objective_id, is_deleted=False).all()
    result = []
    for p in progress_list:
        status = db.session.get(Status, p.status_id)
        try:
            enum = StatusEnum(status.name)
            label = STATUS_LABELS[enum]
        except Exception:
            label = '-'
        result.append({
            'id': p.id,
            'status': label,
            'detail': p.detail,
            'report_date': p.report_date.strftime('%Y-%m-%d'),
            'updated_by': db.session.get(User, p.updated_by).name
        })
    return result, 200


def get_latest_progress(objective_id, user):
    objective = get_objective_by_id(objective_id)
    if not objective:
        return {'error': 'オブジェクティブが見つかりません'}, 404
    task = get_task_by_id(objective.task_id)
    if not task:
        return {'error': 'タスクが見つかりません'}, 404

    if not check_task_access(user, task, TaskAccessLevelEnum.VIEW):
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

    if status:
        try:
            enum = StatusEnum(status.name)
            label = STATUS_LABELS[enum]
        except Exception:
            label = '-'
    else:
        label = '-'

    return {
        'status': label,
        'report_date': progress.report_date.strftime('%Y-%m-%d'),
        'updated_by': user_name,
        'detail': progress.detail
    }, 200


def delete_progress(progress_id, user):
    progress = get_progress_by_id(progress_id)
    if not progress:
        return {'error': '進捗が見つかりません'}, 404
    objective = get_objective_by_id_with_deleted(progress.objective_id)
    if not objective or objective.is_deleted:
        return {'error': 'オブジェクティブが見つかりません'}, 404
    task = get_task_by_id_with_deleted(objective.task_id)
    if not task or task.is_deleted:
        return {'error': 'タスクが見つかりません'}, 404

    if not check_task_access(user, task, TaskAccessLevelEnum.EDIT):
        return {'error': '削除権限がありません'}, 403

    progress.soft_delete()
    db.session.commit()
    return {'message': '進捗を削除しました'}, 200
