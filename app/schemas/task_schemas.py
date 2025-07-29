from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Task
from app.constants import TaskAccessLevelEnum
from app.models import TaskAccessUser, TaskAccessOrganization
from app.constants import StatusEnum
from app import db
from app.models import Status

class TaskSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True
        include_fk = True
        exclude = ("is_deleted",)
    id = fields.Integer(required=True, dump_only=True, allow_none=False)
    user_access_level = fields.Str()
    status = EnumField(StatusEnum, by_value=True, dump_only=True)
    label = fields.Method("get_status_label", dump_only=True)

    def get_status_label(self, obj):
        from app.constants import STATUS_LABELS
        try:
            return STATUS_LABELS[StatusEnum(obj.status.name)]
        except Exception:
            return None

class TaskInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = False
        include_fk = True
        exclude = ("id", "created_by", "created_at", "is_deleted")

    title = fields.Str(required=True)
    description = fields.Str(load_default="")
    due_date = fields.Str(load_default=None)
    status = EnumField(StatusEnum, by_value=True, load_default=StatusEnum.NOT_STARTED)
    display_order = fields.Int(load_default=None)

    @validates_schema
    def resolve_status_enum(self, data, **kwargs):
        if "status" in data and data["status"] is not None:
            status_obj = db.session.query(Status).filter_by(name=data["status"].value).first()
            if not status_obj:
                raise ValidationError("Invalid status value", field_name="status")
            data["status_id"] = status_obj.id

class TaskUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = False
        include_fk = True
        exclude = ("id", "created_by", "created_at", "is_deleted")

    title = fields.Str(required=False)
    description = fields.Str()
    due_date = fields.Str()
    status = EnumField(StatusEnum, by_value=True,
                       metadata={"type": "string", "enum": [e.value for e in StatusEnum]})
    display_order = fields.Int()

    @validates_schema
    def resolve_status_enum(self, data, **kwargs):
        if "status" in data and data["status"] is not None:
            status_obj = db.session.query(Status).filter_by(name=data["status"].value).first()
            if not status_obj:
                raise ValidationError("Invalid status value", field_name="status")
            data["status_id"] = status_obj.id


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
    label = fields.Str()