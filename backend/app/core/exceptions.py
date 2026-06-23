"""Custom exception hierarchy for BluAdmin.

Every exception carries an HTTP status code and a structured detail payload
so that the global exception handler can return consistent JSON error responses.
"""

from typing import Any


class BluAdminError(Exception):
    """Base exception for all BluAdmin domain errors.

    Attributes
    ----------
    message:  Human-readable error description.
    status_code:  HTTP status code the API should return.
    detail:  Optional extra payload included in the JSON response body.
    """

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
    """Raised when an employee lookup returns no results."""

    def __init__(self, employee_id: str | int) -> None:
        super().__init__(
            message=f"Employee not found: {employee_id}",
            status_code=404,
            detail={"employee_id": str(employee_id)},
        )


class GraphAPIError(BluAdminError):
    """Raised when a Microsoft Graph API call fails.

    Returns HTTP 502 (Bad Gateway) because the upstream service is at fault.
    """

    def __init__(self, operation: str, detail: str) -> None:
        super().__init__(
            message=f"Microsoft Graph API error during {operation}: {detail}",
            status_code=502,
            detail={"operation": operation, "graph_detail": detail},
        )


class InsufficientPermissionsError(BluAdminError):
    """Raised when the authenticated user lacks the required role or scope."""

    def __init__(self, message: str = "Insufficient permissions") -> None:
        super().__init__(
            message=message,
            status_code=403,
        )


class ValidationError(BluAdminError):
    """Raised for domain-level validation failures (beyond Pydantic parsing)."""

    def __init__(self, message: str = "Validation error", detail: Any = None) -> None:
        super().__init__(
            message=message,
            status_code=422,
            detail=detail,
        )


class DuplicateEmployeeError(BluAdminError):
    """Raised when creating an employee that already exists."""

    def __init__(
        self,
        message: str = "An employee with the given identifier already exists",
        detail: Any = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=409,
            detail=detail,
        )
