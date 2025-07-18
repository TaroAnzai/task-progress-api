from marshmallow import Schema, fields

class AISuggestInputSchema(Schema):
    task_info = fields.Dict(required=True)
    mode = fields.Str(load_default="task_name")

class JobIdSchema(Schema):
    job_id = fields.Str()

class AIResultSchema(Schema):
    job_id = fields.Str()
    status = fields.Str()
    message = fields.Str(load_default=None)
