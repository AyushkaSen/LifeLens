from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import DashboardOverview
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=DashboardOverview)
def get_dashboard_metrics(
    days: int = Query(7, ge=1, le=30, description="Time window in days"),
    db: Session = Depends(get_db),
):
    return analytics_service.get_dashboard_data(db, days=days)
