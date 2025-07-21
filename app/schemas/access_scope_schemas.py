from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import AccessScope

class AccessScopeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AccessScope
        load_instance = True
        include_fk = True

    role = fields.Function(lambda obj: obj.role.value)

class AccessScopeInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AccessScope
        load_instance = False
        include_fk = True
        exclude = ("id",)

    organization_id = fields.Int(required=True)
    role = fields.Str(required=True)
