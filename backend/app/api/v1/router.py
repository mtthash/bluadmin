"""Aggregates all v1 routers into a single APIRouter."""

from fastapi import APIRouter

from app.api.v1 import (
    audit, auth, dashboard, departments, employees, folder_mappings, health, platform_users, policies, users,
)

api_v1_router = APIRouter()

api_v1_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_v1_router.include_router(health.router, prefix="/health", tags=["Health"])
api_v1_router.include_router(employees.router, prefix="/employees", tags=["Employees"])
api_v1_router.include_router(
    departments.router, prefix="/departments", tags=["Departments"]
)
api_v1_router.include_router(audit.router, prefix="/audit-logs", tags=["Audit"])
api_v1_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_v1_router.include_router(users.router, prefix="/users", tags=["Users"])
api_v1_router.include_router(
    platform_users.router, prefix="/platform-users", tags=["Platform Users"]
)
api_v1_router.include_router(folder_mappings.router)
api_v1_router.include_router(policies.router, prefix="/policies", tags=["Policies"])
