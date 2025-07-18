from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.Int()
    wp_user_id = fields.Int(allow_none=True)
    name = fields.Str()
    email = fields.Str()
    is_superuser = fields.Bool()
    organization_id = fields.Int(allow_none=True)
    organization_name = fields.Str(allow_none=True)

class UserInputSchema(Schema):
    wp_user_id = fields.Int(load_default=None)
    name = fields.Str(required=True)
    email = fields.Str(required=True)
    password = fields.Str(load_default=None)
    role = fields.Str(load_default=None)
    organization_id = fields.Int(required=True)

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
