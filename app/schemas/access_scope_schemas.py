from marshmallow import Schema, fields

class AccessScopeSchema(Schema):
    id = fields.Int()
    organization_id = fields.Int()
    role = fields.Str()

class AccessScopeInputSchema(Schema):
    organization_id = fields.Int(required=True)
    role = fields.Str(required=True)
