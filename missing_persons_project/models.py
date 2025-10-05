from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from sqlalchemy.sql import func
from database import Base

class Volunteer(Base):
    __tablename__ = "volunteers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    experience_years = Column(Integer, nullable=False)
    operations_count = Column(Integer, nullable=False)
    emoji_icon = Column(String(10), nullable=False, default="👤")
    photo_url = Column(String(255), nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class MissingPerson(Base):
    __tablename__ = "missing_persons"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(200), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    last_seen_location = Column(String(255), nullable=False)
    last_seen_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    height = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=True)
    clothing = Column(Text, nullable=True)
    distinguishing_features = Column(Text, nullable=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    contact_name = Column(String(200), nullable=False)
    contact_phone = Column(String(50), nullable=False)
    contact_email = Column(String(100), nullable=True)
    photo_url = Column(String(255), nullable=True)
    status = Column(String(20), default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())