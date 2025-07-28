from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Organization

class OrganizationSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Organization
        load_instance = True
        include_fk = True

    level = fields.Int()

class OrganizationInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Organization
        load_instance = False
        include_fk = True
        exclude = ("id",)

    name = fields.Str(required=True)
    org_code = fields.Str(required=True)
    company_id = fields.Int(load_default=None)
    parent_id = fields.Int(load_default=None)

class OrganizationUpdateSchema(Schema):
    name = fields.Str()
    parent_id = fields.Int(allow_none=True)

class OrganizationTreeSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    org_code = fields.Str()
    company_id = fields.Int()
    company_name = fields.Str()
    parent_id = fields.Int(allow_none=True)
    level = fields.Int()
    children = fields.List(fields.Nested(lambda: OrganizationTreeSchema()))

class OrganizationQuerySchema(Schema):
    company_id = fields.Int(required=True, metadata={"description": "会社ID"})