import os
import uuid
import datetime
from typing import List, Optional
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import ScrapLot, ScrapRate, User, Pickup
from app.schemas import ScrapLotCreate, ScrapLotResponse, ScrapLotRejectRequest
from app.auth import get_optional_user

router = APIRouter(prefix="/scrap", tags=["Scrap Lots & Transactions"])

def get_or_create_default_collector(db: Session) -> User:
    user = db.query(User).filter(User.role == "collector").first()
    if not user:
        user = User(
            mobile="9876543210",
            password_hash="$2b$12$e6xU4mN9m9wZ.placeholder",
            full_name="Scrap Collector",
            role="collector",
            status="Active"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

def get_or_create_default_recycler(db: Session) -> User:
    user = db.query(User).filter(User.role == "recycler").first()
    if not user:
        user = User(
            mobile="9998887770",
            password_hash="$2b$12$e6xU4mN9m9wZ.placeholder",
            full_name="Green Recycling Centre",
            business_name="Green Recycling Centre",
            role="recycler",
            status="Active"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user

@router.post("", response_model=ScrapLotResponse, status_code=status.HTTP_201_CREATED)
def submit_scrap(
    payload: ScrapLotCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Collector submits a new scrap lot.
    """
    collector = current_user if current_user else get_or_create_default_collector(db)

    # Get rate
    rate_row = db.query(ScrapRate).filter(ScrapRate.material.ilike(payload.material.strip())).first()
    rate = rate_row.rate_per_kg if rate_row else 20.0
    price = round(rate * payload.weight, 2)

    # Generate lot number (e.g. LOT-1001)
    last_lot = db.query(ScrapLot).order_by(ScrapLot.id.desc()).first()
    next_id = (last_lot.id + 1) if last_lot else 1001
    lot_number = f"LOT-{next_id:04d}"

    scrap_lot = ScrapLot(
        lot_number=lot_number,
        collector_id=collector.id,
        material=payload.material.strip(),
        weight=payload.weight,
        rate=rate,
        price=price,
        photo_url=payload.photo_url,
        pickup_address=payload.pickup_address or collector.address,
        collector_notes=payload.collector_notes,
        status="Pending"
    )
    db.add(scrap_lot)
    db.commit()
    db.refresh(scrap_lot)
    return scrap_lot

@router.get("/my-collections", response_model=List[ScrapLotResponse])
def get_my_collections(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Retrieve collection history for the current collector.
    If unauthenticated, returns all lots for seamless testing.
    """
    if current_user and current_user.role == "collector":
        return db.query(ScrapLot).filter(ScrapLot.collector_id == current_user.id).order_by(ScrapLot.created_at.desc()).all()
    # Fallback in dev/test: return all lots
    return db.query(ScrapLot).order_by(ScrapLot.created_at.desc()).all()

@router.get("/incoming", response_model=List[ScrapLotResponse])
def get_incoming_lots(db: Session = Depends(get_db)):
    """
    Retrieve all pending scrap lots for recyclers.
    """
    return db.query(ScrapLot).filter(ScrapLot.status == "Pending").order_by(ScrapLot.created_at.desc()).all()

@router.get("/history", response_model=List[ScrapLotResponse])
def get_transaction_history(
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Retrieve transaction history for recyclers (Accepted and Completed lots).
    """
    query = db.query(ScrapLot).filter(ScrapLot.status.in_(["Accepted", "Completed"]))
    if current_user and current_user.role == "recycler":
        query = query.filter(ScrapLot.recycler_id == current_user.id)
    return query.order_by(ScrapLot.accepted_at.desc(), ScrapLot.created_at.desc()).all()

@router.get("/{lot_id}", response_model=ScrapLotResponse)
def get_scrap_lot(lot_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information about a scrap lot by ID.
    """
    lot = db.query(ScrapLot).filter(ScrapLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Scrap lot not found")
    return lot

@router.post("/{lot_id}/accept", response_model=ScrapLotResponse)
def accept_lot(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Recycler accepts an incoming scrap lot. Moves lot to Accepted and schedules pickup.
    """
    lot = db.query(ScrapLot).filter(ScrapLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Scrap lot not found")
    if lot.status != "Pending":
        raise HTTPException(status_code=400, detail=f"Lot is no longer pending (Current status: {lot.status})")

    recycler = current_user if current_user else get_or_create_default_recycler(db)
    lot.status = "Accepted"
    lot.recycler_id = recycler.id
    lot.accepted_at = datetime.datetime.utcnow()

    # Create or update pickup schedule
    existing_pickup = db.query(Pickup).filter(Pickup.scrap_lot_id == lot.id).first()
    if not existing_pickup:
        pickup = Pickup(
            scrap_lot_id=lot.id,
            status="Pickup Scheduled",
            step=2,
            pickup_date=datetime.datetime.utcnow() + datetime.timedelta(days=1),
            vehicle_number="MH-12-SS-2026",
            driver_name="Ramesh Kumar",
            driver_contact="9823012345"
        )
        db.add(pickup)
    else:
        existing_pickup.status = "Pickup Scheduled"
        existing_pickup.step = 2

    db.commit()
    db.refresh(lot)
    return lot

@router.post("/{lot_id}/reject", response_model=ScrapLotResponse)
def reject_lot(
    lot_id: int,
    reject_body: Optional[ScrapLotRejectRequest] = None,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Recycler rejects an incoming scrap lot.
    """
    lot = db.query(ScrapLot).filter(ScrapLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Scrap lot not found")
    if lot.status != "Pending":
        raise HTTPException(status_code=400, detail=f"Cannot reject lot in status '{lot.status}'")

    recycler = current_user if current_user else get_or_create_default_recycler(db)
    lot.status = "Rejected"
    lot.recycler_id = recycler.id
    if reject_body and reject_body.reason:
        lot.recycler_notes = reject_body.reason

    db.commit()
    db.refresh(lot)
    return lot

@router.post("/{lot_id}/handover", response_model=ScrapLotResponse)
def confirm_handover(
    lot_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_user)
):
    """
    Confirm scrap physical handover and complete the transaction.
    """
    lot = db.query(ScrapLot).filter(ScrapLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Scrap lot not found")
    if lot.status != "Accepted":
        raise HTTPException(status_code=400, detail=f"Cannot complete lot with status '{lot.status}'. Must be Accepted first.")

    lot.status = "Completed"
    lot.completed_at = datetime.datetime.utcnow()

    # Update pickup if exists
    pickup = db.query(Pickup).filter(Pickup.scrap_lot_id == lot.id).first()
    if pickup:
        pickup.status = "Completed"
        pickup.step = 4

    db.commit()
    db.refresh(lot)
    return lot

@router.post("/upload-photo")
async def upload_scrap_photo(file: UploadFile = File(...)):
    """
    Upload a scrap photo and return public access URL.
    """
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    extension = os.path.splitext(file.filename)[1] or ".jpg"
    unique_filename = f"{uuid.uuid4()}{extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)

    async with aiofiles.open(file_path, "wb") as buffer:
        content = await file.read()
        await buffer.write(content)

    return {
        "filename": unique_filename,
        "photo_url": f"/uploads/{unique_filename}",
        "size_bytes": len(content)
    }
