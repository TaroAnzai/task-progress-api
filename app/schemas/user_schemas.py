from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import User

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ("password_hash",)
    organization_name = fields.Method("get_org_name")

    def get_org_name(self, obj):
        return obj.organization.name if obj.organization else None

class UserInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        include_fk = True
        exclude = ("id", "password_hash", "is_superuser")

    name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    role = fields.Str()
    organization_id=fields.Int(required=True)

class UserUpdateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        include_fk = True
        exclude = ("id", "password_hash", "is_superuser")

    # すべて任意。ただし形式は検証する
    name = fields.Str(required=False)
    email = fields.Email(required=False)
    password = fields.Str(required=False, load_only=True)
    role = fields.Str(required=False)
    organization_id=fields.Int(required=False)

class UserCreateResponseSchema(Schema):
    message = fields.Str()
    user = fields.Nested(UserSchema)

class LoginResponseSchema(Schema):
    message = fields.Str()
    user = fields.Nested(UserSchema)

class LoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class WPLoginSchema(Schema):
    wp_user_id = fields.Int(required=True)
