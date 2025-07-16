from enum import Enum

class OrgRoleEnum(str, Enum):
    MEMBER = "member"
    ORG_ADMIN = "org_admin"
    SYSTEM_ADMIN = "system_admin"

ORG_ROLE_PRIORITY = {
    OrgRoleEnum.MEMBER: 1,
    OrgRoleEnum.ORG_ADMIN: 2,
    OrgRoleEnum.SYSTEM_ADMIN: 3,
}

class TaskAccessLevelEnum(str, Enum):
    VIEW = "view"
    EDIT = "edit"
    FULL = "full"
    OWNER = "owner"

TASK_ACCESS_PRIORITY = {
    TaskAccessLevelEnum.VIEW: 1,
    TaskAccessLevelEnum.EDIT: 2,
    TaskAccessLevelEnum.FULL: 3,
    TaskAccessLevelEnum.OWNER: 4,
}


class StatusEnum(str, Enum):
    UNDEFINED = "undefined"
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SAVED = "saved"


STATUS_LABELS = {
    StatusEnum.UNDEFINED: "未定義",
    StatusEnum.NOT_STARTED: "未着手",
    StatusEnum.IN_PROGRESS: "進行中",
    StatusEnum.COMPLETED: "完了",
    StatusEnum.SAVED: "保存",
}
