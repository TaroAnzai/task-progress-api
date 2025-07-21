from marshmallow import Schema, fields

class MessageSchema(Schema):
    message = fields.Str()

class YAMLResponseSchema(Schema):
    yaml = fields.Str()

class ValidationErrorField(Schema):
    # errors["json"] に相当する部分
    # 任意のキーとリストを許可
    class Meta:
        unknown = "INCLUDE"

class ErrorResponseSchema(Schema):
    code = fields.Int(required=True)
    status = fields.Str(required=True)
    errors = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(ValidationErrorField),
        required=True
    )