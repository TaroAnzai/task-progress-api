class ServiceError(ValueError):
    """Base class for service layer errors."""
    status_code = 500  # デフォルトはサーバーエラー

    def __init__(self, message: str = None):
        super().__init__(message or self.__doc__)

class ServiceValidationError(ServiceError):
    """Bad request from service layer."""
    status_code = 400
    
class ServiceAuthenticationError(ServiceError):
    """Authentication failure from service layer."""
    status_code = 401
class ServicePermissionError(ServiceError):
    """Permission failure from service layer."""
    status_code = 403


class ServiceNotFoundError(ServiceError):
    """Resource not found in service layer."""
    status_code = 404


class ServiceConflictError(ServiceError):
    """Conflict with current state or duplicated resource."""
    status_code = 409
