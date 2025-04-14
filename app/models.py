from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import uuid4
import time

class Position(BaseModel):
    lat: float
    lon: float

class CachedPosition(BaseModel):
    value: Position
    timestamp: int
    cache: str = "miss"

class CachedStatus(BaseModel):
    value: str = "mantenimiento"
    timestamp: int
    cache: str = "miss"

class Satellite(BaseModel):
    id: str
    position: CachedPosition
    status: CachedStatus
    radius: float = Field(..., ge=1000, le=5000)
    speed: float = Field(..., ge=10000, le=30000)
    direction: float

class SatelliteCreateRequest(BaseModel):
    position: Position
    direction: float
    speed: float
    radius: float

class Pagination(BaseModel):
    current_page: int
    per_page: int
    total_items: int
    total_pages: int
    next_page: Optional[int]
    prev_page: Optional[int]

class PaginatedSatellites(BaseModel):
    data: List[Satellite]
    pagination: Pagination