from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from app.constants import TaskAccessLevelEnum

class AccessUserSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    email = fields.Str()
    access_level = EnumField(TaskAccessLevelEnum, by_value=True)

class OrgAccessSchema(Schema):
    organization_id = fields.Int()
    name = fields.Str()
    access_level = EnumField(TaskAccessLevelEnum, by_value=True)

class _AccessUserInputSchema(Schema):
    user_id = fields.Int(required=True)
    access_level = EnumField(TaskAccessLevelEnum, by_value=True, required=True)

class _AccessOrgInputSchema(Schema):
    organization_id = fields.Int(required=True)
    access_level = EnumField(TaskAccessLevelEnum, by_value=True, required=True)

class AccessLevelInputSchema(Schema):
    user_access = fields.List(fields.Nested(_AccessUserInputSchema), required=True)
    organization_access = fields.List(fields.Nested(_AccessOrgInputSchema), required=True)
