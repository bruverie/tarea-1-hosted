from fastapi import APIRouter, HTTPException, Header, Query, Path
from app.cache import get_or_update_position, get_or_update_status
from typing import Optional
from uuid import uuid4

from app.models import (
    SatelliteCreateRequest,
    Satellite,
    CachedPosition,
    CachedStatus,
    PaginatedSatellites,
    Pagination
)
from app.cache import get_or_update_position, get_or_update_status

router = APIRouter()

# Almacén temporal de satélites
satellites_db = {}


@router.post("/satellites", response_model=Satellite, status_code=201)
async def create_satellite(
    data: SatelliteCreateRequest,
    x_timestamp: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None)
):
    if not x_timestamp or not x_timestamp.isdigit():
        raise HTTPException(status_code=400, detail="Missing or invalid X-Timestamp")
    if not x_request_id:
        raise HTTPException(status_code=400, detail="Missing X-Request-ID")

    timestamp = int(x_timestamp)
    sat_id = str(uuid4())

    satellite = Satellite(
        id=sat_id,
        position=CachedPosition(
            value=data.position,
            timestamp=timestamp,
            cache="miss"
        ),
        status=CachedStatus(
            value="mantenimiento",
            timestamp=timestamp,
            cache="miss"
        ),
        radius=data.radius,
        speed=data.speed,
        direction=data.direction
    )

    satellites_db[sat_id] = {
        "satellite": satellite,
        "created_at": timestamp
    }

    return satellite


@router.get("/satellites", response_model=PaginatedSatellites)
async def get_satellites(
    page: int = Query(1, ge=1),
    x_timestamp: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None)
):
    if not x_timestamp or not x_timestamp.isdigit():
        raise HTTPException(status_code=400, detail="Missing or invalid X-Timestamp")
    if not x_request_id:
        raise HTTPException(status_code=400, detail="Missing X-Request-ID")

    t_actual = int(x_timestamp)

    all_satellites = list(satellites_db.values())
    total_items = len(all_satellites)
    per_page = 10
    total_pages = (total_items + per_page - 1) // per_page

    start = (page - 1) * per_page
    end = start + per_page
    selected = all_satellites[start:end]

    updated_data = []
    for registro in selected:
        sat = registro["satellite"]
        t_creado = registro["created_at"]

        sat.position = get_or_update_position(sat, t_actual, t_creado)
        sat.status = await get_or_update_status(sat, t_actual)

        updated_data.append(sat)

    pagination = Pagination(
        current_page=page,
        per_page=per_page,
        total_items=total_items,
        total_pages=total_pages,
        next_page=page + 1 if page < total_pages else None,
        prev_page=page - 1 if page > 1 else None
    )

    return PaginatedSatellites(data=updated_data, pagination=pagination)


@router.get("/satellites/{satellite_id}", response_model=Satellite)
async def get_satellite_by_id(
    satellite_id: str = Path(...),
    x_timestamp: Optional[str] = Header(None),
    x_request_id: Optional[str] = Header(None)
):
    if not x_timestamp or not x_timestamp.isdigit():
        raise HTTPException(status_code=400, detail="Missing or invalid X-Timestamp")
    if not x_request_id:
        raise HTTPException(status_code=400, detail="Missing X-Request-ID")

    if satellite_id not in satellites_db:
        raise HTTPException(status_code=404, detail=f"satellite with id {satellite_id} not found")

    registro = satellites_db[satellite_id]
    sat = registro["satellite"]
    t_creado = registro["created_at"]
    t_actual = int(x_timestamp)

    sat.position = get_or_update_position(sat, t_actual, t_creado)
    sat.status = await get_or_update_status(sat, t_actual)

    return sat

@router.post("/reset")
async def reset_satellites():
    satellites_db.clear()
    return {"message": "ok"}