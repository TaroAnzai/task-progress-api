class ServiceValidationError(ValueError):
    """Bad request from service layer."""
    pass

class ServiceAuthenticationError(ValueError):
    """Authentication failure from service layer."""
    pass

class ServicePermissionError(ValueError):
    """Permission failure from service layer."""
    pass

class ServiceNotFoundError(ValueError):
    """Resource not found in service layer."""
    pass

