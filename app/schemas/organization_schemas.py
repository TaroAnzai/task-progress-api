from marshmallow import Schema, fields

class OrganizationSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    org_code = fields.Str()
    company_id = fields.Int()
    parent_id = fields.Int(allow_none=True)
    level = fields.Int()

class OrganizationInputSchema(Schema):
    name = fields.Str(required=True)
    org_code = fields.Str(required=True)
    company_id = fields.Int(load_default=None)
    parent_id = fields.Int(load_default=None)

class OrganizationUpdateSchema(Schema):
    name = fields.Str()
    parent_id = fields.Int(allow_none=True)
