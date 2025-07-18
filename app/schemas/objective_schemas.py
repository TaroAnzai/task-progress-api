from marshmallow import Schema, fields

class ObjectiveSchema(Schema):
    id = fields.Int()
    task_id = fields.Int()
    title = fields.Str()
    due_date = fields.Str(allow_none=True)
    assigned_user_id = fields.Int(allow_none=True)
    status_id = fields.Int()
    created_by = fields.Int()
    created_at = fields.Str()

class ObjectiveInputSchema(Schema):
    task_id = fields.Int(required=True)
    title = fields.Str(required=True)
    due_date = fields.Str(load_default=None)
    assigned_user_id = fields.Int(load_default=None)
    status_id = fields.Int(load_default=None)

class ObjectiveResponseSchema(Schema):
    message = fields.Str()
    objective = fields.Nested(ObjectiveSchema)

class ObjectivesListSchema(Schema):
    objectives = fields.List(fields.Nested(ObjectiveSchema))

class StatusSchema(Schema):
    id = fields.Int()
    label = fields.Str()
