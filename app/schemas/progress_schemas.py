from marshmallow import Schema, fields
from app.constants import StatusEnum
from marshmallow_enum import EnumField

class ProgressInputSchema(Schema):
    status = EnumField(StatusEnum, load_default=StatusEnum.NOT_STARTED, required=False,
                       metadata={"type": "string", "enum": [e.name for e in StatusEnum]})
    detail = fields.Str(required=True)
    report_date = fields.DateTime(required=True)

class ProgressSchema(Schema):
    id = fields.Integer(required=True, dump_only=True, allow_none=False)
    status = EnumField(StatusEnum, dump_only=True, metadata={"type": "string", "enum": [e.name for e in StatusEnum]})
    detail = fields.Str()
    report_date = fields.Date()
    updated_by =  fields.String()
