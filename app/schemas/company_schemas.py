from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import Schema, fields
from app.models import Company

class CompanySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        include_fk = True
        load_instance = True
        exclude = ("is_deleted",)
    id = fields.Integer(required=True, dump_only=True, allow_none=False)

class CompanyInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        load_instance = False
        exclude = ("id", "is_deleted")

class DeleteCompanyQuerySchema(Schema):
    force = fields.Bool(
        load_default=False,
        metadata={"description": "trueなら物理削除、falseなら論理削除"}
    )

class DeleteCompanyQuerySchema(Schema):
    force = fields.Bool(
        load_default=False,
        metadata={"description": "trueなら物理削除、falseなら論理削除"}
    )
class CompanyQuerySchema(Schema):
    with_deleted = fields.Bool(
        load_default=False,
        metadata={"description": "trueなら論理削除済みも含めて取得"}
    )