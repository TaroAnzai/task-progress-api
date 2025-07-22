# app/services/objectives_service.py
from datetime import datetime
from app.models import db, Objective, Task, Status
from app.utils import check_task_access, is_valid_status_id
from app.constants import TaskAccessLevelEnum, StatusEnum, STATUS_LABELS
from app.service_errors import (
    ServiceValidationError,
    ServicePermissionError,
    ServiceNotFoundError,
)


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
        raise ServiceValidationError('タイトル・タスクIDは必須です')

    task = get_task_by_id(task_id)
    if not task:
        raise ServiceNotFoundError('タスクが見つかりません')
    if not check_task_access(user, task, TaskAccessLevelEnum.EDIT):
        raise ServicePermissionError('このタスクにオブジェクティブを追加する権限がありません')

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            raise ServiceValidationError('日付の形式が正しくありません（YYYY-MM-DD）')

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
        'objective': objective,
    }


def update_objective(objective_id, data, user):
    objective = get_objective_by_id(objective_id)
    if not objective:
        raise ServiceNotFoundError('オブジェクティブが見つかりません')
    task = get_task_by_id(objective.task_id)
    if not task:
        raise ServiceNotFoundError('タスクが見つかりません')

    if not check_task_access(user, task, TaskAccessLevelEnum.EDIT):
        raise ServicePermissionError('編集権限がありません')

    objective.title = data.get('title', objective.title)
    if 'due_date' in data:
        try:
            objective.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            raise ServiceValidationError('日付の形式が正しくありません（YYYY-MM-DD）')
    if 'assigned_user_id' in data:
        objective.assigned_user_id = data['assigned_user_id']
    if 'status_id' in data:
        if not is_valid_status_id(data['status_id']):
            raise ServiceValidationError('ステータスIDが不正です')
        objective.status_id = data['status_id']

    db.session.commit()
    return {
        'message': 'オブジェクティブを更新しました',
        'objective': objective
        }


def get_objectives_for_task(task_id, user):
    task = get_task_by_id(task_id)
    if not task:
        raise ServiceNotFoundError('タスクが見つかりません')
    if not check_task_access(user, task, TaskAccessLevelEnum.VIEW):
        raise ServicePermissionError('閲覧権限がありません')

    objectives = Objective.query.filter_by(task_id=task_id, is_deleted=False) \
                                 .order_by(Objective.display_order).all()
    
    return {'objectives': objectives}


def get_objective(objective_id, user):
    objective = get_objective_by_id(objective_id)
    if not objective:
        raise ServiceNotFoundError('オブジェクティブが見つかりません')

    task = get_task_by_id(objective.task_id)
    if not task:
        raise ServiceNotFoundError('タスクが見つかりません')
    if not check_task_access(user, task, TaskAccessLevelEnum.VIEW):
        raise ServicePermissionError('閲覧権限がありません')

    return objective


def delete_objective(objective_id, user):
    objective = get_objective_by_id(objective_id)
    if not objective:
        raise ServiceNotFoundError('オブジェクティブが見つかりません')
    task = get_task_by_id(objective.task_id)
    if not task:
        raise ServiceNotFoundError('タスクが見つかりません')

    if not check_task_access(user, task, TaskAccessLevelEnum.EDIT):
        raise ServicePermissionError('削除権限がありません')

    objective.soft_delete()
    db.session.commit()

    remaining = Objective.query.filter_by(task_id=task.id, is_deleted=False) \
                                .order_by(Objective.display_order).all()
    for idx, obj in enumerate(remaining):
        obj.display_order = idx
    db.session.commit()

    return {'message': 'オブジェクティブを削除し、順序を更新しました'}

