from marshmallow import Schema, fields

class TaskSchema(Schema):
    id = fields.Int()
    status_id = fields.Int(allow_none=True)
    title = fields.Str()
    description = fields.Str()
    due_date = fields.Str(allow_none=True)
    assigned_user_id = fields.Int(allow_none=True)
    created_by = fields.Int()
    created_at = fields.Str()
    display_order = fields.Int(allow_none=True)
    organization_id = fields.Int()

class TaskInputSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(load_default="")
    due_date = fields.Str(load_default=None)
    status_id = fields.Int(load_default=None)
    display_order = fields.Int(load_default=None)

class TaskCreateResponseSchema(Schema):
    message = fields.Str()
    task = fields.Nested(TaskSchema)

class TaskListResponseSchema(Schema):
    tasks = fields.List(fields.Nested(TaskSchema))

class OrderSchema(Schema):
    order = fields.List(fields.Int(), required=True)

class TaskOrderSchema(Schema):
    task_id = fields.Int()
    title = fields.Str()

class TaskOrderInputSchema(Schema):
    task_ids = fields.List(fields.Int(), required=True)
