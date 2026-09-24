import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    mobile = Column(String(20), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="collector")  # "collector", "recycler", "admin"
    business_name = Column(String(150), nullable=True)
    address = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    status = Column(String(20), default="Active")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    submitted_lots = relationship("ScrapLot", back_populates="collector", foreign_keys="ScrapLot.collector_id")
    accepted_lots = relationship("ScrapLot", back_populates="recycler", foreign_keys="ScrapLot.recycler_id")


class ScrapRate(Base):
    __tablename__ = "scrap_rates"

    id = Column(Integer, primary_key=True, index=True)
    material = Column(String(50), unique=True, index=True, nullable=False)
    rate_per_kg = Column(Float, nullable=False)
    unit = Column(String(10), default="kg")
    currency = Column(String(5), default="₹")
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ScrapLot(Base):
    __tablename__ = "scrap_lots"

    id = Column(Integer, primary_key=True, index=True)
    lot_number = Column(String(30), unique=True, index=True, nullable=False)
    collector_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    recycler_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    material = Column(String(50), nullable=False)
    weight = Column(Float, nullable=False)
    rate = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    photo_url = Column(String(255), nullable=True)
    status = Column(String(20), default="Pending")  # Pending, Accepted, Rejected, Completed
    pickup_address = Column(String(255), nullable=True)
    collector_notes = Column(Text, nullable=True)
    recycler_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    collector = relationship("User", foreign_keys=[collector_id], back_populates="submitted_lots")
    recycler = relationship("User", foreign_keys=[recycler_id], back_populates="accepted_lots")
    pickup = relationship("Pickup", back_populates="scrap_lot", uselist=False, cascade="all, delete-orphan")


class Pickup(Base):
    __tablename__ = "pickups"

    id = Column(Integer, primary_key=True, index=True)
    scrap_lot_id = Column(Integer, ForeignKey("scrap_lots.id"), unique=True, nullable=False)
    status = Column(String(30), default="Pickup Scheduled")  # Pickup Scheduled, Handover Pending, Completed, Cancelled
    step = Column(Integer, default=2)  # 1: Lot Accepted, 2: Pickup Scheduled, 3: Handover Pending, 4: Completed
    pickup_date = Column(DateTime, nullable=True)
    vehicle_number = Column(String(50), nullable=True)
    driver_name = Column(String(100), nullable=True)
    driver_contact = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    scrap_lot = relationship("ScrapLot", back_populates="pickup")
