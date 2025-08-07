from marshmallow import Schema, fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Task
from app.constants import StatusEnum
from app import db

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        include_fk = True
        exclude = ("is_deleted",)
    id = fields.Integer(required=True, dump_only=True, allow_none=False)
    user_access_level = fields.Str()
    status =  fields.Enum(StatusEnum, by_value=False, dump_only=True ,
                       metadata={"type": "string", "enum": [e.name for e in StatusEnum]})

class TaskInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = False
        include_fk = True
        exclude = ("id", "created_by", "created_at", "is_deleted")

    title = fields.Str(required=True)
    description = fields.Str(load_default="")
    due_date = fields.Str(load_default=None)
    status =  fields.Enum(StatusEnum, by_value=False, load_default=StatusEnum.UNDEFINED,
                       metadata={"type": "string", "enum": [e.name for e in StatusEnum]})
    display_order = fields.Int(load_default=None)



class TaskUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = False
        include_fk = True
        exclude = ("id", "created_by", "created_at", "is_deleted")

    title = fields.Str(required=False)
    description = fields.Str()
    due_date = fields.Str()
    status =  fields.Enum(StatusEnum, by_value=False,
                       metadata={"type": "string", "enum": [e.name for e in StatusEnum]})
    display_order = fields.Int()

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
    user_id = fields.Int(required=True)

class StatusSchema(Schema):
    id = fields.Int()
    enum = fields.Str()
    label = fields.Str()