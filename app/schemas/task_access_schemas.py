from marshmallow import Schema, fields

class AccessUserSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    access_level = fields.Str()

class OrgAccessSchema(Schema):
    organization_id = fields.Int()
    name = fields.Str()
    access_level = fields.Str()

class AccessLevelInputSchema(Schema):
    user_access = fields.List(fields.Dict(), required=True)
    organization_access = fields.List(fields.Dict(), required=True)
