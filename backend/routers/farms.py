"""
routers/farms.py
----------------
FastAPI router for Farm management endpoints.

Endpoints:
    POST   /farms          → Create a new farm
    GET    /farms          → List all farms (paginated)
    GET    /farms/{id}     → Get a single farm
    PATCH  /farms/{id}     → Update farm details
    DELETE /farms/{id}     → Delete a farm
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/farms",
    tags=["Farms"],
    responses={404: {"description": "Farm not found"}},
)


# ─── POST /farms ──────────────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=schemas.FarmOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new farm",
    description="Create a new farm record with farmer name and location.",
)
def create_farm(
    farm_in: schemas.FarmCreate,
    db: Session = Depends(get_db),
) -> schemas.FarmOut:
    """
    Register a new farm.

    - **farmer_name**: Full name of the farmer (2–150 characters)
    - **location**: Village, district, or city name
    """
    logger.info("POST /farms | farmer=%s location=%s", farm_in.farmer_name, farm_in.location)
    farm = crud.create_farm(db=db, farm_in=farm_in)
    return farm


# ─── GET /farms ───────────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[schemas.FarmOut],
    summary="List all farms",
    description="Retrieve all registered farms with optional pagination.",
)
def list_farms(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> List[schemas.FarmOut]:
    """Return a paginated list of all farms."""
    logger.info("GET /farms | skip=%s limit=%s", skip, limit)
    return crud.get_all_farms(db=db, skip=skip, limit=limit)


# ─── GET /farms/{farm_id} ─────────────────────────────────────────────────────
@router.get(
    "/{farm_id}",
    response_model=schemas.FarmOut,
    summary="Get a farm by ID",
)
def get_farm(
    farm_id: int,
    db: Session = Depends(get_db),
) -> schemas.FarmOut:
    """Retrieve a single farm by its ID."""
    logger.info("GET /farms/%s", farm_id)
    farm = crud.get_farm(db=db, farm_id=farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id={farm_id} not found.",
        )
    return farm


# ─── PATCH /farms/{farm_id} ───────────────────────────────────────────────────
@router.patch(
    "/{farm_id}",
    response_model=schemas.FarmOut,
    summary="Update farm details",
    description="Partially update a farm record. Only provided fields are updated.",
)
def update_farm(
    farm_id: int,
    farm_update: schemas.FarmUpdate,
    db: Session = Depends(get_db),
) -> schemas.FarmOut:
    """Partially update a farm (PATCH semantics)."""
    logger.info("PATCH /farms/%s", farm_id)
    updated = crud.update_farm(db=db, farm_id=farm_id, farm_update=farm_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id={farm_id} not found.",
        )
    return updated


# ─── DELETE /farms/{farm_id} ──────────────────────────────────────────────────
@router.delete(
    "/{farm_id}",
    response_model=schemas.MessageResponse,
    summary="Delete a farm",
    description="Delete a farm and all its associated soil records (cascade).",
)
def delete_farm(
    farm_id: int,
    db: Session = Depends(get_db),
) -> schemas.MessageResponse:
    """Delete a farm by ID."""
    logger.info("DELETE /farms/%s", farm_id)
    deleted = crud.delete_farm(db=db, farm_id=farm_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id={farm_id} not found.",
        )
    return schemas.MessageResponse(message=f"Farm id={farm_id} deleted successfully.")
