import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

# ================= AUTH & USER SCHEMAS =================
class UserBase(BaseModel):
    mobile: str = Field(..., description="Mobile number with or without country code")
    full_name: str
    role: str = Field("collector", description="'collector', 'recycler', or 'admin'")
    business_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=4)

class UserLogin(BaseModel):
    mobile: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    business_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None

class UserResponse(UserBase):
    id: int
    status: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ================= RATE SCHEMAS =================
class ScrapRateBase(BaseModel):
    material: str
    rate_per_kg: float
    unit: str = "kg"
    currency: str = "₹"

class ScrapRateCreate(ScrapRateBase):
    pass

class ScrapRateUpdate(BaseModel):
    rate_per_kg: float

class ScrapRateResponse(ScrapRateBase):
    id: int
    updated_at: datetime.datetime

    class Config:
        from_attributes = True


# ================= PICKUP SCHEMAS =================
class PickupResponse(BaseModel):
    id: int
    scrap_lot_id: int
    status: str
    step: int
    pickup_date: Optional[datetime.datetime] = None
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class PickupUpdate(BaseModel):
    status: Optional[str] = None
    step: Optional[int] = None
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    driver_contact: Optional[str] = None


# ================= SCRAP LOT SCHEMAS =================
class ScrapLotCreate(BaseModel):
    material: str
    weight: float = Field(..., gt=0, description="Weight in kg")
    photo_url: Optional[str] = None
    pickup_address: Optional[str] = None
    collector_notes: Optional[str] = None

class ScrapLotResponse(BaseModel):
    id: int
    lot_number: str
    collector_id: int
    recycler_id: Optional[int] = None
    material: str
    weight: float
    rate: float
    price: float
    photo_url: Optional[str] = None
    status: str
    pickup_address: Optional[str] = None
    collector_notes: Optional[str] = None
    recycler_notes: Optional[str] = None
    created_at: datetime.datetime
    accepted_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    collector: Optional[UserResponse] = None
    recycler: Optional[UserResponse] = None
    pickup: Optional[PickupResponse] = None

    class Config:
        from_attributes = True

class ScrapLotRejectRequest(BaseModel):
    reason: Optional[str] = None


# ================= DASHBOARD SCHEMAS =================
class MaterialBreakdown(BaseModel):
    material: str
    total_kg: float
    total_value: float

class DashboardStatsResponse(BaseModel):
    total_lots: int
    pending_lots: int
    accepted_lots: int
    completed_lots: int
    total_weight_kg: float
    total_value_rs: float
    materials_breakdown: List[MaterialBreakdown]
