from flask import current_app
from datetime import datetime
from app.models import db, Task, Objective, UserTaskOrder, TaskAccessUser, TaskAccessOrganization
from app.utils import check_task_access, is_valid_status_id
from app.constants import TaskAccessLevelEnum
from app.service_errors import (
    ServiceValidationError,
    ServicePermissionError,
    ServiceAuthenticationError,
    ServiceNotFoundError,
)
from sqlalchemy import and_, or_


def get_task_by_id(task_id):
    return Task.query.filter_by(id=task_id, is_deleted=False).first()


def get_task_by_id_with_deleted(task_id):
    return db.session.get(Task, task_id)

def create_task(data, user):
    title = data.get('title')
    if not title:
        raise ServiceValidationError('タイトルは必須です')

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            raise ServiceValidationError('日付の形式が正しくありません（YYYY-MM-DD）')

    task = Task(
        title=title,
        description=data.get('description', ''),
        due_date=due_date,
        created_by=user.id,
        organization_id=user.organization_id
    )
    db.session.add(task)
    db.session.flush()

    db.session.query(UserTaskOrder).filter_by(user_id=user.id).update(
        {UserTaskOrder.display_order: UserTaskOrder.display_order + 1},
        synchronize_session='fetch'
    )
    db.session.add(UserTaskOrder(user_id=user.id, task_id=task.id, display_order=0))
    db.session.commit()

    return task


def update_task(task_id, data, user):
    task = get_task_by_id(task_id)
    if not task:
        raise ServiceNotFoundError('タスクが見つかりません')
    if not check_task_access(user, task, TaskAccessLevelEnum.FULL):
        raise ServicePermissionError('このタスクを編集する権限がありません')

    if 'status_id' in data:
        if not is_valid_status_id(data['status_id']):
            raise ServiceValidationError('ステータスIDが不正です')
        task.status_id = data['status_id']
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'due_date' in data:
        try:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            raise ServiceValidationError('日付の形式が正しくありません（YYYY-MM-DD）')
    if 'display_order' in data:
        task.display_order = data['display_order']

    db.session.commit()
    return task

def delete_task(task_id, user):
    task = get_task_by_id(task_id)
    if not task:
        raise ServiceNotFoundError('タスクが見つかりません')
    if not check_task_access(user, task, TaskAccessLevelEnum.FULL):
        raise ServicePermissionError('このタスクを削除する権限がありません')

    orders = UserTaskOrder.query.filter_by(task_id=task_id).all()
    for order in orders:
        db.session.delete(order)
    db.session.flush()

    TaskAccessUser.query.filter_by(task_id=task_id).delete()
    TaskAccessOrganization.query.filter_by(task_id=task_id).delete()

    task.soft_delete()
    db.session.commit()

def get_tasks(user):
    current_app.logger.info("[START] get_tasks called")

    if not user or not user.is_authenticated:
        raise ServiceAuthenticationError('ログインが必要です')

    org_id = user.organization_id
    user_id = user.id

    filter_conditions = [
        Task.created_by == user_id,
        Task.id.in_(
            db.session.query(TaskAccessUser.task_id)
            .filter(TaskAccessUser.user_id == user_id)
            .filter(TaskAccessUser.access_level.in_([
                TaskAccessLevelEnum.VIEW,
                TaskAccessLevelEnum.EDIT,
                TaskAccessLevelEnum.FULL,
            ]))
        ),
        Task.id.in_(
            db.session.query(TaskAccessOrganization.task_id)
            .filter(TaskAccessOrganization.organization_id == org_id)
            .filter(
                TaskAccessOrganization.access_level.in_([
                    TaskAccessLevelEnum.VIEW,
                    TaskAccessLevelEnum.EDIT,
                    TaskAccessLevelEnum.FULL,
                ])
            )
        )
    ]

    visible_tasks = (
        db.session.query(Task, UserTaskOrder.display_order.label('user_order'))
        .outerjoin(UserTaskOrder, and_(
            UserTaskOrder.task_id == Task.id,
            UserTaskOrder.user_id == user_id
        ))
        .filter(
            and_(
                Task.is_deleted != True,
                or_(*filter_conditions)
            )
        )
        .order_by(
            UserTaskOrder.display_order.is_(None),
            UserTaskOrder.display_order.asc().nullslast(),
            Task.display_order.asc().nullslast()
        )
        .all()
    )

    result = []
    for task, user_order in visible_tasks:
        task.user_access_level = _calc_user_access_level(task, user_id, org_id)
        task.display_order = user_order if user_order is not None else task.display_order
        result.append(task)
    return result

def _calc_user_access_level(task, user_id, org_id):
    if task.created_by == user_id:
        return TaskAccessLevelEnum.FULL.value
    if (entry := TaskAccessUser.query.filter_by(task_id=task.id, user_id=user_id).first()):
        return entry.access_level.value
    if (entry := TaskAccessOrganization.query.filter_by(task_id=task.id, organization_id=org_id).first()):
        return entry.access_level.value
    return TaskAccessLevelEnum.VIEW.value

def update_objective_order(task_id, data):
    new_order = data.get('order')
    if not new_order or not isinstance(new_order, list):
        raise ServiceValidationError('order はオブジェクティブIDのリストである必要があります')

    objectives = Objective.query.filter_by(task_id=task_id).filter(Objective.is_deleted != True).all()
    obj_dict = {obj.id: obj for obj in objectives}

    for index, obj_id in enumerate(new_order):
        obj = obj_dict.get(obj_id)
        if obj:
            obj.display_order = index
        else:
            raise ServiceNotFoundError(f'Objective ID {obj_id} が見つかりません')

    db.session.commit()
    return {'message': '表示順を更新しました'}
