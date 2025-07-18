from marshmallow import Schema, fields

class ProgressInputSchema(Schema):
    status_id = fields.Int(required=True)
    detail = fields.Str(required=True)
    report_date = fields.Str(required=True)

class ProgressSchema(Schema):
    id = fields.Int()
    status = fields.Str()
    detail = fields.Str()
    report_date = fields.Str()
    updated_by = fields.Str()
