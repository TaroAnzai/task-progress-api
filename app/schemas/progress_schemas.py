from marshmallow import Schema, fields
from app.constants import StatusEnum
from marshmallow_enum import EnumField

class ProgressInputSchema(Schema):
    status = EnumField(StatusEnum, by_value=True, load_default=StatusEnum.NOT_STARTED, required = False,
                       metadata={"type": "string", "enum": [e.value for e in StatusEnum]})

    detail = fields.Str(required=True)
    report_date = fields.Str(required=True)

class ProgressSchema(Schema):
    id = fields.Integer(required=True, dump_only=True, allow_none=False)
    status = fields.Str()
    detail = fields.Str()
    report_date = fields.Str()
    updated_by = fields.Str()
