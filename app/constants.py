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
