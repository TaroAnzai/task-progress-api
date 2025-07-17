from flask import jsonify, current_app
from datetime import datetime
from app.models import db, Task, Objective, UserTaskOrder, TaskAccessUser, TaskAccessOrganization
from app.utils import check_task_access, is_valid_status_id
from app.constants import TaskAccessLevelEnum
from sqlalchemy import and_, or_


def get_task_by_id(task_id):
    return Task.query.filter_by(id=task_id, is_deleted=False).first()


def get_task_by_id_with_deleted(task_id):
    return db.session.get(Task, task_id)

def create_task(data, user):
    title = data.get('title')
    if not title:
        return jsonify({'error': 'タイトルは必須です'}), 400

    due_date = None
    if data.get('due_date'):
        try:
            due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '日付の形式が正しくありません（YYYY-MM-DD）'}), 400

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

    return jsonify({'message': 'タスクを追加しました', 'task': task.to_dict()}), 201


def update_task(task_id, data, user):
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({'error': 'タスクが見つかりません'}), 404
    if not check_task_access(user, task, TaskAccessLevelEnum.FULL):
        return jsonify({'error': 'このタスクを編集する権限がありません'}), 403

    if 'status_id' in data:
        if not is_valid_status_id(data['status_id']):
            return jsonify({'error': 'ステータスIDが不正です'}), 400
        task.status_id = data['status_id']
    if 'title' in data:
        task.title = data['title']
    if 'description' in data:
        task.description = data['description']
    if 'due_date' in data:
        try:
            task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': '日付の形式が正しくありません（YYYY-MM-DD）'}), 400
    if 'display_order' in data:
        task.display_order = data['display_order']

    db.session.commit()
    return jsonify({'message': 'タスクを更新しました'})

def delete_task(task_id, user):
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({'error': 'タスクが見つかりません'}), 404
    if not check_task_access(user, task, TaskAccessLevelEnum.FULL):
        return jsonify({'error': 'このタスクを削除する権限がありません'}), 403

    orders = UserTaskOrder.query.filter_by(task_id=task_id).all()
    for order in orders:
        db.session.delete(order)
    db.session.flush()

    TaskAccessUser.query.filter_by(task_id=task_id).delete()
    TaskAccessOrganization.query.filter_by(task_id=task_id).delete()

    task.soft_delete()
    db.session.commit()
    return jsonify({'message': 'タスクを削除しました'})

def get_tasks(user):
    current_app.logger.info("[START] get_tasks called")

    if not user or not user.is_authenticated:
        return jsonify({'error': 'ログインが必要です'}), 401

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
        task_dict = task.to_dict()
        task_dict['display_order'] = user_order if user_order is not None else task.display_order

        if task.created_by == user_id:
            task_dict['user_access_level'] = TaskAccessLevelEnum.FULL.value
        elif (entry := TaskAccessUser.query.filter_by(task_id=task.id, user_id=user_id).first()):
            task_dict['user_access_level'] = entry.access_level.value
        elif (entry := TaskAccessOrganization.query.filter_by(task_id=task.id, organization_id=org_id).first()):
            task_dict['user_access_level'] = entry.access_level.value
        else:
            task_dict['user_access_level'] = TaskAccessLevelEnum.VIEW.value

        result.append(task_dict)

    return {'tasks': result}, 200

def update_objective_order(task_id, data):
    new_order = data.get('order')
    if not new_order or not isinstance(new_order, list):
        return jsonify({'error': 'order はオブジェクティブIDのリストである必要があります'}), 400

    objectives = Objective.query.filter_by(task_id=task_id).filter(Objective.is_deleted != True).all()
    obj_dict = {obj.id: obj for obj in objectives}

    for index, obj_id in enumerate(new_order):
        obj = obj_dict.get(obj_id)
        if obj:
            obj.display_order = index
        else:
            return jsonify({'error': f'Objective ID {obj_id} が見つかりません'}), 404

    db.session.commit()
    return jsonify({'message': '表示順を更新しました'})
