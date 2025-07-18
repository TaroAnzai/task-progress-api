from marshmallow import Schema, fields

class MessageSchema(Schema):
    message = fields.Str()

class ErrorResponseSchema(Schema):
    message = fields.Str()

class YAMLResponseSchema(Schema):
    yaml = fields.Str()
