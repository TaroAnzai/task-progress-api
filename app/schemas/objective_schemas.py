from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Objective, Status

class ObjectiveSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Objective
        load_instance = True
        include_fk = True
        exclude = ("is_deleted",)

    id = fields.Integer(required=True, dump_only=True, allow_none=False)
    assigned_user_name = fields.String(dump_only=True)
    latest_progress = fields.String(dump_only=True, allow_none=True)
    latest_report_date = fields.DateTime(dump_only=True, allow_none=True)

class ObjectiveInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Objective
        load_instance = False
        include_fk = True
        exclude = ("id", "created_by", "created_at", "display_order", "is_deleted")

    task_id = fields.Int(required=True)
    title = fields.Str(required=True)
    due_date = fields.Str(load_default=None)
    assigned_user_id = fields.Int(load_default=None)
    status_id = fields.Int(load_default=None)
class ObjectiveUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Objective
        load_instance = False
        include_fk = True
        exclude = ("id", "created_by", "created_at", "display_order", "is_deleted")

    task_id = fields.Int()
    title = fields.Str()
    due_date = fields.Str()
    assigned_user_id = fields.Int()
    status_id = fields.Int()

class ObjectiveResponseSchema(Schema):
    message = fields.Str()
    objective = fields.Nested(ObjectiveSchema)

class ObjectivesListSchema(Schema):
    objectives = fields.List(fields.Nested(ObjectiveSchema))


