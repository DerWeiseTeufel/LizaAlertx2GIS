from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VolunteerResponse(BaseModel):
    id: int
    name: str
    role: str
    description: str
    experience_years: int
    operations_count: int
    emoji_icon: str
    photo_url: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class MissingPersonResponse(BaseModel):
    id: int
    full_name: str
    age: int
    gender: str
    last_seen_location: str
    last_seen_date: datetime
    description: str
    latitude: float
    longitude: float
    contact_name: str
    contact_phone: str
    photo_url: Optional[str]
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True