from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import ScrapLot
from app.schemas import DashboardStatsResponse, MaterialBreakdown

router = APIRouter(prefix="/dashboard", tags=["Dashboard & Analytics"])

@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Get system-wide or operational dashboard stats for ScrapSetu.
    """
    total_lots = db.query(ScrapLot).count()
    pending_lots = db.query(ScrapLot).filter(ScrapLot.status == "Pending").count()
    accepted_lots = db.query(ScrapLot).filter(ScrapLot.status == "Accepted").count()
    completed_lots = db.query(ScrapLot).filter(ScrapLot.status == "Completed").count()

    total_weight = db.query(func.coalesce(func.sum(ScrapLot.weight), 0.0)).scalar()
    total_val = db.query(func.coalesce(func.sum(ScrapLot.price), 0.0)).scalar()

    # Material breakdown
    materials_query = (
        db.query(
            ScrapLot.material,
            func.coalesce(func.sum(ScrapLot.weight), 0.0).label("total_kg"),
            func.coalesce(func.sum(ScrapLot.price), 0.0).label("total_value")
        )
        .group_by(ScrapLot.material)
        .all()
    )

    breakdown = [
        MaterialBreakdown(
            material=row[0],
            total_kg=round(float(row[1]), 2),
            total_value=round(float(row[2]), 2)
        )
        for row in materials_query
    ]

    return DashboardStatsResponse(
        total_lots=total_lots,
        pending_lots=pending_lots,
        accepted_lots=accepted_lots,
        completed_lots=completed_lots,
        total_weight_kg=round(float(total_weight), 2),
        total_value_rs=round(float(total_val), 2),
        materials_breakdown=breakdown
    )
