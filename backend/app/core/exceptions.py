"""Custom exception hierarchy for BluAdmin."""

from typing import Any


class BluAdminError(Exception):
    def __init__(
        self,
        message: str = "An internal error occurred",
        status_code: int = 500,
        detail: Any = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class EmployeeNotFoundError(BluAdminError):
    def __init__(self, employee_id: str | int) -> None:
        super().__init__(
            message=f"Employee not found: {employee_id}",
            status_code=404,
            detail={"employee_id": str(employee_id)},
        )


class LDAPOperationError(BluAdminError):
    def __init__(self, operation: str, detail: str) -> None:
        super().__init__(
            message=f"LDAP operation error during {operation}: {detail}",
            status_code=502,
            detail={"operation": operation, "ldap_detail": detail},
        )


class InsufficientPermissionsError(BluAdminError):
    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(message=message, status_code=403)


class ValidationError(BluAdminError):
    def __init__(self, message: str = "Validation error", detail: Any = None) -> None:
        super().__init__(message=message, status_code=422, detail=detail)


class DuplicateEmployeeError(BluAdminError):
    def __init__(
        self,
        message: str = "An employee with the given identifier already exists",
        detail: Any = None,
    ) -> None:
        super().__init__(message=message, status_code=409, detail=detail)


class DuplicateDepartmentError(BluAdminError):
    def __init__(self, name: str) -> None:
        super().__init__(
            message=f"Já existe um departamento com o nome '{name}'",
            status_code=409,
            detail={"name": name},
        )
