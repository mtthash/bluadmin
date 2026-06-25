"""Dashboard statistics endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select, extract, case, literal
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.department import Department
from app.models.audit_log import AuditLog

router = APIRouter()


class DepartmentCount(BaseModel):
    name: str
    count: int


class MonthlyActivity(BaseModel):
    month: str
    onboards: int
    offboards: int


class StatusCount(BaseModel):
    status: str
    count: int


class RecentAction(BaseModel):
    action: str
    actor_email: str | None
    target_email: str | None
    result: str | None
    created_at: datetime


class DashboardStats(BaseModel):
    employees_by_department: list[DepartmentCount]
    monthly_activity: list[MonthlyActivity]
    status_counts: list[StatusCount]
    recent_actions: list[RecentAction]


@router.get(
    "/",
    response_model=DashboardStats,
    dependencies=[Depends(get_current_user)],
)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
) -> DashboardStats:
    employees_by_dept = await _get_employees_by_department(db)
    monthly = await _get_monthly_activity(db)
    statuses = await _get_status_counts(db)
    recent = await _get_recent_actions(db)

    return DashboardStats(
        employees_by_department=employees_by_dept,
        monthly_activity=monthly,
        status_counts=statuses,
        recent_actions=recent,
    )


async def _get_employees_by_department(db: AsyncSession) -> list[DepartmentCount]:
    stmt = (
        select(
            func.coalesce(User.department, "Sem departamento").label("dept"),
            func.count(User.id).label("total"),
        )
        .where(User.status == "active")
        .group_by("dept")
        .order_by(func.count(User.id).desc())
    )
    result = await db.execute(stmt)
    return [DepartmentCount(name=row.dept, count=row.total) for row in result.all()]


async def _get_monthly_activity(db: AsyncSession) -> list[MonthlyActivity]:
    now = datetime.now(timezone.utc)
    six_months_ago = now - timedelta(days=180)

    stmt = (
        select(
            func.to_char(AuditLog.created_at, "YYYY-MM").label("month"),
            func.sum(
                case((AuditLog.action == "user.onboard", 1), else_=0)
            ).label("onboards"),
            func.sum(
                case((AuditLog.action == "user.offboard", 1), else_=0)
            ).label("offboards"),
        )
        .where(
            AuditLog.created_at >= six_months_ago,
            AuditLog.action.in_(["user.onboard", "user.offboard"]),
            AuditLog.result == "success",
        )
        .group_by("month")
        .order_by("month")
    )
    result = await db.execute(stmt)
    return [
        MonthlyActivity(month=row.month, onboards=row.onboards, offboards=row.offboards)
        for row in result.all()
    ]


async def _get_status_counts(db: AsyncSession) -> list[StatusCount]:
    stmt = (
        select(User.status, func.count(User.id).label("total"))
        .group_by(User.status)
    )
    result = await db.execute(stmt)

    label_map = {"active": "Ativos", "disabled": "Desabilitados"}
    return [
        StatusCount(status=label_map.get(row.status, row.status), count=row.total)
        for row in result.all()
    ]


async def _get_recent_actions(db: AsyncSession) -> list[RecentAction]:
    stmt = (
        select(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    return [
        RecentAction(
            action=log.action,
            actor_email=log.actor_email,
            target_email=log.target_email,
            result=log.result,
            created_at=log.created_at,
        )
        for log in result.scalars().all()
    ]
