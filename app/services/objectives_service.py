# app/services/objectives_service.py
from flask import jsonify
from datetime import datetime
from app.models import db, Objective, Task, Status
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


def create_objective(data, user):
    title = data.get('title')
    task_id = data.get('task_id')

    if not title or not task_id:
        return {'error': 'タイトル・タスクIDは必須です'}, 400

    task = get_task_by_id(task_id)
    if not task:
        return {'error': 'タスクが見つかりません'}, 404
    if not check_task_access(user, task, TaskAccessLevelEnum.EDIT):
        return {'error': 'このタスクにオブジェクティブを追加する権限がありません'}, 403

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            return {'error': '日付の形式が正しくありません（YYYY-MM-DD）'}, 400

    max_order = db.session.query(db.func.max(Objective.display_order)) \
        .filter_by(task_id=task_id).scalar()
    new_order = (max_order or 0) + 1

    objective = Objective(
        task_id=task_id,
        title=title,
        due_date=due_date,
        assigned_user_id=data.get('assigned_user_id'),
        display_order=new_order
    )

    db.session.add(objective)
    db.session.commit()

    return {
        'message': 'オブジェクティブを追加しました',
        'objective': objective.to_dict(),
        'display_order': objective.display_order
    }, 201


def update_objective(objective_id, data, user):
    objective = get_objective_by_id(objective_id)
    if not objective:
        return {'error': 'オブジェクティブが見つかりません'}, 404
    task = get_task_by_id(objective.task_id)
    if not task:
        return {'error': 'タスクが見つかりません'}, 404

    if not check_task_access(user, task, TaskAccessLevelEnum.EDIT):
        return {'error': '編集権限がありません'}, 403

    objective.title = data.get('title', objective.title)
    if 'due_date' in data:
        try:
            objective.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            return {'error': '日付の形式が正しくありません（YYYY-MM-DD）'}, 400
    if 'assigned_user_id' in data:
        objective.assigned_user_id = data['assigned_user_id']
    if 'status_id' in data:
        if not is_valid_status_id(data['status_id']):
            return {'error': 'ステータスIDが不正です'}, 400
        objective.status_id = data['status_id']

    db.session.commit()
    return {'message': 'オブジェクティブを更新しました', 'objective': objective.to_dict()}, 200


def get_objectives_for_task(task_id, user):
    task = get_task_by_id(task_id)
    if not task:
        return {'error': 'タスクが見つかりません'}, 404
    if not check_task_access(user, task, TaskAccessLevelEnum.VIEW):
        return {'error': '閲覧権限がありません'}, 403

    objectives = Objective.query.filter_by(task_id=task_id, is_deleted=False) \
                                 .order_by(Objective.display_order).all()
    return [
        {
            'id': obj.id,
            'title': obj.title,
            'due_date': obj.due_date.strftime('%Y-%m-%d') if obj.due_date else None,
            'assigned_user_id': obj.assigned_user_id,
            'status_id': obj.status_id,
            'display_order': obj.display_order,
            'task_id': obj.task_id,
            'created_at': obj.created_at
        } for obj in objectives
    ], 200


def get_objective(objective_id, user):
    objective = get_objective_by_id(objective_id)
    if not objective:
        return {'error': 'オブジェクティブが見つかりません'}, 404

    task = get_task_by_id(objective.task_id)
    if not task:
        return {'error': 'タスクが見つかりません'}, 404
    if not check_task_access(user, task, TaskAccessLevelEnum.VIEW):
        return {'error': '閲覧権限がありません'}, 403

    return {
        'id': objective.id,
        'task_id': objective.task_id,
        'title': objective.title,
        'due_date': objective.due_date.strftime('%Y-%m-%d') if objective.due_date else None,
        'assigned_user_id': objective.assigned_user_id,
        'status_id': objective.status_id
    }, 200


def delete_objective(objective_id, user):
    objective = get_objective_by_id(objective_id)
    if not objective:
        return {'error': 'オブジェクティブが見つかりません'}, 404
    task = get_task_by_id(objective.task_id)
    if not task:
        return {'error': 'タスクが見つかりません'}, 404

    if not check_task_access(user, task, TaskAccessLevelEnum.EDIT):
        return {'error': '削除権限がありません'}, 403

    objective.soft_delete()
    db.session.commit()

    remaining = Objective.query.filter_by(task_id=task.id, is_deleted=False) \
                                .order_by(Objective.display_order).all()
    for idx, obj in enumerate(remaining):
        obj.display_order = idx
    db.session.commit()

    return {'message': 'オブジェクティブを削除し、順序を更新しました'}, 200


def get_statuses():
    statuses = Status.query.all()
    result = []
    for s in statuses:
        try:
            enum = StatusEnum(s.name)
        except ValueError:
            continue
        result.append({'id': s.id, 'label': STATUS_LABELS[enum]})
    return result
