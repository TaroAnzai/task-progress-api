from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import Company

class CompanySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        include_fk = True
        load_instance = True
        exclude = ("is_deleted",)

class CompanyInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Company
        load_instance = False
        exclude = ("id", "is_deleted")