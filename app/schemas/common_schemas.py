from marshmallow import Schema, fields

class MessageSchema(Schema):
    message = fields.Str()

class ErrorResponseSchema(Schema):
    error = fields.Str()

class YAMLResponseSchema(Schema):
    yaml = fields.Str()
