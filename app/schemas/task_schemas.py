from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Task

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        include_fk = True
        exclude = ("is_deleted",)

class TaskInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = False
        include_fk = True
        exclude = ("id", "created_by", "created_at", "is_deleted")

    title = fields.Str(required=True)
    description = fields.Str(load_default="")
    due_date = fields.Str(load_default=None)
    status_id = fields.Int(load_default=None)
    display_order = fields.Int(load_default=None)

class TaskCreateResponseSchema(Schema):
    message = fields.Str()
    task = fields.Nested(TaskSchema)

class TaskListResponseSchema(Schema):
    tasks = fields.List(fields.Nested(TaskSchema))

class OrderSchema(Schema):
    order = fields.List(fields.Int(), required=True)

class TaskOrderSchema(Schema):
    task_id = fields.Int()
    title = fields.Str()

class TaskOrderInputSchema(Schema):
    task_ids = fields.List(fields.Int(), required=True)
