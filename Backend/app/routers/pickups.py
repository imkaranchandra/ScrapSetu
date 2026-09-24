from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pickup, ScrapLot, User
from app.schemas import PickupResponse, PickupUpdate, ScrapLotResponse
from app.auth import get_optional_user

router = APIRouter(prefix="/pickups", tags=["Pickups & Logistics"])

@router.get("/active", response_model=Optional[ScrapLotResponse])
def get_active_pickup(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Get the latest active scheduled pickup (Lot status == 'Accepted').
    """
    query = db.query(ScrapLot).filter(ScrapLot.status == "Accepted")
    if current_user and current_user.role == "recycler":
        query = query.filter(ScrapLot.recycler_id == current_user.id)
    latest = query.order_by(ScrapLot.accepted_at.desc()).first()
    return latest

@router.get("/{lot_id}", response_model=PickupResponse)
def get_pickup_details(lot_id: int, db: Session = Depends(get_db)):
    """
    Get logistics pickup record for a specific scrap lot.
    """
    pickup = db.query(Pickup).filter(Pickup.scrap_lot_id == lot_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="No pickup record found for this scrap lot")
    return pickup

@router.patch("/{lot_id}", response_model=PickupResponse)
def update_pickup(
    lot_id: int,
    pickup_data: PickupUpdate,
    db: Session = Depends(get_db)
):
    """
    Update pickup driver, vehicle, status or tracking step.
    """
    pickup = db.query(Pickup).filter(Pickup.scrap_lot_id == lot_id).first()
    if not pickup:
        raise HTTPException(status_code=404, detail="No pickup record found for this scrap lot")

    if pickup_data.status is not None:
        pickup.status = pickup_data.status
    if pickup_data.step is not None:
        pickup.step = pickup_data.step
    if pickup_data.vehicle_number is not None:
        pickup.vehicle_number = pickup_data.vehicle_number
    if pickup_data.driver_name is not None:
        pickup.driver_name = pickup_data.driver_name
    if pickup_data.driver_contact is not None:
        pickup.driver_contact = pickup_data.driver_contact

    db.commit()
    db.refresh(pickup)
    return pickup
