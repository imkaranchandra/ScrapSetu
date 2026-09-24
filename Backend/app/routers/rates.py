from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ScrapRate, User
from app.schemas import ScrapRateResponse, ScrapRateCreate, ScrapRateUpdate
from app.auth import get_optional_user

router = APIRouter(prefix="/rates", tags=["Rates"])

DEFAULT_RATES = {
    "Plastic": 20.0,
    "Paper": 15.0,
    "Iron": 35.0,
    "Copper": 600.0,
    "Aluminium": 120.0,
    "Steel": 45.0,
    "E-Waste": 80.0
}

def seed_default_rates_if_empty(db: Session):
    count = db.query(ScrapRate).count()
    if count == 0:
        for material, rate in DEFAULT_RATES.items():
            db.add(ScrapRate(
                material=material,
                rate_per_kg=rate,
                unit="kg",
                currency="₹"
            ))
        db.commit()

@router.get("", response_model=List[ScrapRateResponse])
def get_all_rates(db: Session = Depends(get_db)):
    """
    Get all scrap material rates.
    """
    seed_default_rates_if_empty(db)
    return db.query(ScrapRate).order_by(ScrapRate.material.asc()).all()

@router.get("/dict", response_model=Dict[str, float])
def get_rates_dictionary(db: Session = Depends(get_db)):
    """
    Get rates as a simple key-value dictionary (e.g. {"Plastic": 20, "Iron": 35}).
    Convenient for direct frontend consumption.
    """
    seed_default_rates_if_empty(db)
    rates = db.query(ScrapRate).all()
    return {r.material: r.rate_per_kg for r in rates}

@router.put("/{material}", response_model=ScrapRateResponse)
def update_rate(
    material: str,
    rate_update: ScrapRateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Update scrap rate for a specific material.
    """
    rate_item = db.query(ScrapRate).filter(ScrapRate.material.ilike(material.strip())).first()
    if not rate_item:
        rate_item = ScrapRate(
            material=material.strip().capitalize(),
            rate_per_kg=rate_update.rate_per_kg,
            unit="kg",
            currency="₹"
        )
        db.add(rate_item)
    else:
        rate_item.rate_per_kg = rate_update.rate_per_kg

    db.commit()
    db.refresh(rate_item)
    return rate_item

@router.post("", response_model=ScrapRateResponse, status_code=status.HTTP_201_CREATED)
def create_rate(
    rate_in: ScrapRateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_optional_user)
):
    """
    Add a new scrap rate material or update existing.
    """
    existing = db.query(ScrapRate).filter(ScrapRate.material.ilike(rate_in.material.strip())).first()
    if existing:
        existing.rate_per_kg = rate_in.rate_per_kg
        db.commit()
        db.refresh(existing)
        return existing

    new_rate = ScrapRate(
        material=rate_in.material.strip(),
        rate_per_kg=rate_in.rate_per_kg,
        unit=rate_in.unit,
        currency=rate_in.currency
    )
    db.add(new_rate)
    db.commit()
    db.refresh(new_rate)
    return new_rate
