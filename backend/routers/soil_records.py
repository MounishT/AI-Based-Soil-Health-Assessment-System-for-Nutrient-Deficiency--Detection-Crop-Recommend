"""
routers/soil_records.py
-----------------------
FastAPI router for Soil Record management endpoints.

Endpoints:
    POST   /soil-records               → Create a new soil record
    GET    /soil-records               → List all soil records (paginated, filterable)
    GET    /soil-records/{id}          → Get a single soil record
    PATCH  /soil-records/{id}          → Update a soil record
    DELETE /soil-records/{id}          → Delete a soil record
    GET    /soil-records/farm/{farm_id}→ Get all records for a specific farm
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/soil-records",
    tags=["Soil Records"],
    responses={404: {"description": "Soil record not found"}},
)


# ─── POST /soil-records ───────────────────────────────────────────────────────
@router.post(
    "/",
    response_model=schemas.SoilRecordOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new soil record",
    description=(
        "Submit soil readings for a farm. "
        "ML predictions (crop & fertilizer) are NOT triggered automatically here — "
        "use POST /predict/crop and POST /predict/fertilizer to run predictions."
    ),
)
def create_soil_record(
    record_in: schemas.SoilRecordCreate,
    db: Session = Depends(get_db),
) -> schemas.SoilRecordOut:
    """
    Create a new soil record.

    Validates that the referenced farm_id and image_id (if provided) exist
    before inserting the record.
    """
    logger.info("POST /soil-records | farm_id=%s", record_in.farm_id)

    # ── Validate FK: farm must exist ──────────────────────────────────────
    farm = crud.get_farm(db=db, farm_id=record_in.farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id={record_in.farm_id} not found. Create the farm first.",
        )

    # ── Validate FK: image must exist if provided ─────────────────────────
    if record_in.image_id is not None:
        image = crud.get_image(db=db, image_id=record_in.image_id)
        if not image:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Image with id={record_in.image_id} not found.",
            )

    record = crud.create_soil_record(db=db, record_in=record_in)
    return record


# ─── GET /soil-records ────────────────────────────────────────────────────────
@router.get(
    "/",
    response_model=List[schemas.SoilRecordOut],
    summary="List all soil records",
    description="Retrieve all soil records with optional pagination and farm filter.",
)
def list_soil_records(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    farm_id: Optional[int] = Query(None, gt=0, description="Filter by farm ID"),
    db: Session = Depends(get_db),
) -> List[schemas.SoilRecordOut]:
    """Return a paginated list of soil records, optionally filtered by farm."""
    logger.info("GET /soil-records | skip=%s limit=%s farm_id=%s", skip, limit, farm_id)
    return crud.get_all_soil_records(db=db, skip=skip, limit=limit, farm_id=farm_id)


# ─── GET /soil-records/farm/{farm_id} ────────────────────────────────────────
@router.get(
    "/farm/{farm_id}",
    response_model=List[schemas.SoilRecordOut],
    summary="Get all soil records for a specific farm",
)
def get_records_by_farm(
    farm_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> List[schemas.SoilRecordOut]:
    """Retrieve all soil records belonging to a specific farm."""
    logger.info("GET /soil-records/farm/%s", farm_id)

    # Verify the farm exists
    farm = crud.get_farm(db=db, farm_id=farm_id)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Farm with id={farm_id} not found.",
        )

    return crud.get_all_soil_records(db=db, skip=skip, limit=limit, farm_id=farm_id)


# ─── GET /soil-records/{record_id} ───────────────────────────────────────────
@router.get(
    "/{record_id}",
    response_model=schemas.SoilRecordOut,
    summary="Get a soil record by ID",
)
def get_soil_record(
    record_id: int,
    db: Session = Depends(get_db),
) -> schemas.SoilRecordOut:
    """Retrieve a single soil record by its ID."""
    logger.info("GET /soil-records/%s", record_id)
    record = crud.get_soil_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Soil record with id={record_id} not found.",
        )
    return record


# ─── PATCH /soil-records/{record_id} ─────────────────────────────────────────
@router.patch(
    "/{record_id}",
    response_model=schemas.SoilRecordOut,
    summary="Update a soil record",
    description="Partially update a soil record. Only provided fields are updated.",
)
def update_soil_record(
    record_id: int,
    record_update: schemas.SoilRecordUpdate,
    db: Session = Depends(get_db),
) -> schemas.SoilRecordOut:
    """Partially update a soil record (PATCH semantics)."""
    logger.info("PATCH /soil-records/%s", record_id)
    updated = crud.update_soil_record(db=db, record_id=record_id, record_update=record_update)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Soil record with id={record_id} not found.",
        )
    return updated


# ─── DELETE /soil-records/{record_id} ────────────────────────────────────────
@router.delete(
    "/{record_id}",
    response_model=schemas.MessageResponse,
    summary="Delete a soil record",
)
def delete_soil_record(
    record_id: int,
    db: Session = Depends(get_db),
) -> schemas.MessageResponse:
    """Delete a soil record by ID."""
    logger.info("DELETE /soil-records/%s", record_id)
    deleted = crud.delete_soil_record(db=db, record_id=record_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Soil record with id={record_id} not found.",
        )
    return schemas.MessageResponse(message=f"Soil record id={record_id} deleted successfully.")
