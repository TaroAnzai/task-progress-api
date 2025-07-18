from marshmallow import Schema, fields

class CompanySchema(Schema):
    id = fields.Int()
    name = fields.Str()

class CompanyInputSchema(Schema):
    name = fields.Str(required=True)
