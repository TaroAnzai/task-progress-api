from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import AccessScope
from app.constants import OrgRoleEnum

class AccessScopeSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AccessScope
        load_instance = True
        include_fk = True

    role = EnumField(OrgRoleEnum, by_value=True, required=True,
                    metadata={"type": "string", "enum": [e.value for e in OrgRoleEnum]}
    )

class AccessScopeInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AccessScope
        load_instance = False
        include_fk = True
        exclude = ("id",)

    organization_id = fields.Int(required=True)
    role = EnumField(OrgRoleEnum, by_value=True, required=True,
                    metadata={"type": "string", "enum": [e.value for e in OrgRoleEnum]}
    )
