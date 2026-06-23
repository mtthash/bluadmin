"""Health check endpoint -- no authentication required."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def health_check() -> dict:
    """Return service health status."""
    return {"status": "healthy", "version": "1.0.0"}
