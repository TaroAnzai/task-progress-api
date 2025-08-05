from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models import User
from app.constants import OrgRoleEnum
from app.schemas.access_scope_schemas import AccessScopeSchema

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        include_fk = True
        exclude = ("password_hash",)
    id = fields.Integer(required=True, dump_only=True, allow_none=False)
    organization_id = fields.Integer(required=True, allow_none=False)
    organization_name = fields.Method("get_org_name", required=True, dump_only=True, allow_none=False, metadata={"type": "string"})
    company_id = fields.Integer(required=True, allow_none=False)

    def get_org_name(self, obj):
        return obj.organization.name if obj.organization else None
    
class UserWithScopesSchema(UserSchema):
    access_scopes = fields.Nested(AccessScopeSchema, many=True, dump_only=True, allow_none=True)

class UserInputSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = False
        include_fk = True
        exclude = ("id", "password_hash", "is_superuser")

    name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
    role = EnumField(OrgRoleEnum, by_value=False,
                     metadata={"type": "string", "enum": [e.name for e in OrgRoleEnum]}
    )
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
    role = EnumField(OrgRoleEnum, by_value=False, required=False,
                     metadata={"type": "string", "enum": [e.name for e in OrgRoleEnum]}
    )
    organization_id=fields.Int(required=False)

class UserCreateResponseSchema(Schema):
    message = fields.Str()
    user = fields.Nested(UserSchema, required=True, allow_none=False)

class LoginResponseSchema(Schema):
    message = fields.Str()
    user = fields.Nested(UserSchema)

class LoginSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True)

class WPLoginSchema(Schema):
    wp_user_id = fields.Int(required=True)

class UserByEmailQuerySchema(Schema):
    email = fields.Email(
        required=True,
        metadata={"description": "取得対象のユーザーのメールアドレス"}
    )

class UserByWPIDQuerySchema(Schema):
    wp_user_id = fields.Int(
        required=True,
        metadata={"description": "取得対象のユーザーのWordPressユーザーID"}
    )

class UserQuerySchema(Schema):
    company_id = fields.Int(required=False, metadata={"description": "対象の会社ID（スーパーユーザーのみ）"})