"""
crud.py
-------
Repository layer — all database Create / Read / Update / Delete operations
for the AI-Based Soil Health Assessment System.

Each function accepts a SQLAlchemy Session and returns ORM model instances.
Business logic and HTTP concerns live in the routers / services layer.
"""

import logging
from typing import Optional
from collections import Counter

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend import models
from backend import schemas

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE CRUD
# ══════════════════════════════════════════════════════════════════════════════

def create_image(db: Session, image_in: schemas.ImageCreate) -> models.Image:
    """
    Insert a new image record into the database.

    Args:
        db       : Active database session.
        image_in : Validated ImageCreate schema (filename + filepath).

    Returns:
        The newly created Image ORM instance (with id + uploaded_at populated).
    """
    db_image = models.Image(
        filename=image_in.filename,
        filepath=image_in.filepath,
    )
    db.add(db_image)
    db.commit()
    db.refresh(db_image)   # reload to get server-generated values (id, uploaded_at)
    logger.info("Image created | id=%s filename=%s", db_image.id, db_image.filename)
    return db_image


def get_image(db: Session, image_id: int) -> Optional[models.Image]:
    """
    Fetch a single image by primary key.

    Returns:
        Image ORM instance or None if not found.
    """
    return db.query(models.Image).filter(models.Image.id == image_id).first()


def get_all_images(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Image]:
    """
    Return a paginated list of all images.

    Args:
        skip  : Number of records to skip (for pagination).
        limit : Maximum records to return.
    """
    return db.query(models.Image).offset(skip).limit(limit).all()


def delete_image(db: Session, image_id: int) -> Optional[models.Image]:
    """
    Delete an image record by id (cascades to soil_records via ORM).

    Returns:
        Deleted Image instance, or None if not found.
    """
    db_image = get_image(db, image_id)
    if db_image:
        db.delete(db_image)
        db.commit()
        logger.info("Image deleted | id=%s", image_id)
    return db_image


def count_images(db: Session) -> int:
    """Return total count of image records."""
    return db.query(func.count(models.Image.id)).scalar()


# ══════════════════════════════════════════════════════════════════════════════
# FARM CRUD
# ══════════════════════════════════════════════════════════════════════════════

def create_farm(db: Session, farm_in: schemas.FarmCreate) -> models.Farm:
    """
    Insert a new farm record.

    Args:
        db      : Active database session.
        farm_in : Validated FarmCreate schema.

    Returns:
        Newly created Farm ORM instance.
    """
    db_farm = models.Farm(
        farmer_name=farm_in.farmer_name,
        location=farm_in.location,
    )
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    logger.info("Farm created | id=%s farmer=%s", db_farm.id, db_farm.farmer_name)
    return db_farm


def get_farm(db: Session, farm_id: int) -> Optional[models.Farm]:
    """Fetch a single farm by primary key."""
    return db.query(models.Farm).filter(models.Farm.id == farm_id).first()


def get_all_farms(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[models.Farm]:
    """Return a paginated list of all farms."""
    return db.query(models.Farm).offset(skip).limit(limit).all()


def update_farm(
    db: Session,
    farm_id: int,
    farm_update: schemas.FarmUpdate,
) -> Optional[models.Farm]:
    """
    Partially update a farm record (PATCH semantics — only set fields are updated).

    Returns:
        Updated Farm instance, or None if not found.
    """
    db_farm = get_farm(db, farm_id)
    if not db_farm:
        return None

    # Only update fields that were explicitly provided (not None)
    update_data = farm_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_farm, field, value)

    db.commit()
    db.refresh(db_farm)
    logger.info("Farm updated | id=%s", farm_id)
    return db_farm


def delete_farm(db: Session, farm_id: int) -> Optional[models.Farm]:
    """
    Delete a farm record (cascades to soil_records).

    Returns:
        Deleted Farm instance, or None if not found.
    """
    db_farm = get_farm(db, farm_id)
    if db_farm:
        db.delete(db_farm)
        db.commit()
        logger.info("Farm deleted | id=%s", farm_id)
    return db_farm


def count_farms(db: Session) -> int:
    """Return total count of farm records."""
    return db.query(func.count(models.Farm.id)).scalar()


# ══════════════════════════════════════════════════════════════════════════════
# SOIL RECORD CRUD
# ══════════════════════════════════════════════════════════════════════════════

def create_soil_record(
    db: Session,
    record_in: schemas.SoilRecordCreate,
) -> models.SoilRecord:
    """
    Insert a new soil record (without predictions — predictions are added separately).

    Args:
        db        : Active database session.
        record_in : Validated SoilRecordCreate schema.

    Returns:
        Newly created SoilRecord ORM instance.
    """
    db_record = models.SoilRecord(
        farm_id=record_in.farm_id,
        image_id=record_in.image_id,
        nitrogen=record_in.nitrogen,
        phosphorus=record_in.phosphorus,
        potassium=record_in.potassium,
        temperature=record_in.temperature,
        humidity=record_in.humidity,
        ph=record_in.ph,
        rainfall=record_in.rainfall,
        moisture=record_in.moisture,
        soil_type=record_in.soil_type,
        crop_type=record_in.crop_type,
        notes=record_in.notes,
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    logger.info("SoilRecord created | id=%s farm_id=%s", db_record.id, db_record.farm_id)
    return db_record


def get_soil_record(db: Session, record_id: int) -> Optional[models.SoilRecord]:
    """Fetch a single soil record by primary key."""
    return db.query(models.SoilRecord).filter(models.SoilRecord.id == record_id).first()


def get_all_soil_records(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    farm_id: Optional[int] = None,
) -> list[models.SoilRecord]:
    """
    Return a paginated list of soil records, optionally filtered by farm_id.

    Args:
        skip    : Pagination offset.
        limit   : Max records to return.
        farm_id : If provided, filter records to this farm only.
    """
    query = db.query(models.SoilRecord)
    if farm_id is not None:
        query = query.filter(models.SoilRecord.farm_id == farm_id)
    return query.order_by(models.SoilRecord.created_at.desc()).offset(skip).limit(limit).all()


def update_soil_record_predictions(
    db: Session,
    record_id: int,
    crop_prediction: Optional[str] = None,
    fertilizer_prediction: Optional[str] = None,
) -> Optional[models.SoilRecord]:
    """
    Store ML prediction results on an existing soil record.

    Called by the prediction service after the model returns a result.

    Args:
        record_id             : ID of the soil record to update.
        crop_prediction       : Crop name predicted by the crop model.
        fertilizer_prediction : Fertilizer name predicted by the fertilizer model.

    Returns:
        Updated SoilRecord, or None if record not found.
    """
    db_record = get_soil_record(db, record_id)
    if not db_record:
        return None

    if crop_prediction is not None:
        db_record.crop_prediction = crop_prediction
    if fertilizer_prediction is not None:
        db_record.fertilizer_prediction = fertilizer_prediction

    db.commit()
    db.refresh(db_record)
    logger.info(
        "Predictions saved | record_id=%s crop=%s fertilizer=%s",
        record_id, crop_prediction, fertilizer_prediction,
    )
    return db_record


def update_soil_record(
    db: Session,
    record_id: int,
    record_update: schemas.SoilRecordUpdate,
) -> Optional[models.SoilRecord]:
    """
    Partially update a soil record (PATCH semantics).

    Returns:
        Updated SoilRecord, or None if not found.
    """
    db_record = get_soil_record(db, record_id)
    if not db_record:
        return None

    update_data = record_update.model_dump(exclude_unset=True, by_alias=False)
    for field, value in update_data.items():
        setattr(db_record, field, value)

    db.commit()
    db.refresh(db_record)
    logger.info("SoilRecord updated | id=%s", record_id)
    return db_record


def delete_soil_record(db: Session, record_id: int) -> Optional[models.SoilRecord]:
    """
    Delete a soil record by id.

    Returns:
        Deleted SoilRecord, or None if not found.
    """
    db_record = get_soil_record(db, record_id)
    if db_record:
        db.delete(db_record)
        db.commit()
        logger.info("SoilRecord deleted | id=%s", record_id)
    return db_record


def count_predictions(db: Session) -> int:
    """
    Count soil records that have at least one ML prediction stored.
    Used in the dashboard summary.
    """
    return (
        db.query(func.count(models.SoilRecord.id))
        .filter(
            (models.SoilRecord.crop_prediction.isnot(None))
            | (models.SoilRecord.fertilizer_prediction.isnot(None))
        )
        .scalar()
    )


# ══════════════════════════════════════════════════════════════════════════════
# PREDICTION HISTORY
# ══════════════════════════════════════════════════════════════════════════════

def get_prediction_history(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[dict]:
    """
    Return a flattened prediction history list joining SoilRecord → Image → Farm.

    Returns:
        List of dicts with keys: record_id, image, farm, crop, fertilizer, date.
    """
    records = (
        db.query(models.SoilRecord)
        .filter(
            (models.SoilRecord.crop_prediction.isnot(None))
            | (models.SoilRecord.fertilizer_prediction.isnot(None))
        )
        .order_by(models.SoilRecord.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    history = []
    for r in records:
        history.append(
            {
                "record_id": r.id,
                "image": r.image.filename if r.image else None,
                "farm": r.farm.farmer_name if r.farm else None,
                "crop": r.crop_prediction,
                "fertilizer": r.fertilizer_prediction,
                "date": r.created_at,
            }
        )
    return history


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD AGGREGATIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_dashboard_stats(db: Session) -> schemas.DashboardOut:
    """
    Compute aggregated statistics for the dashboard endpoint.

    Returns:
        DashboardOut schema with total counts and top predictions.
    """
    total_images = count_images(db)
    total_farms = count_farms(db)
    total_predictions = count_predictions(db)

    # ── Top crop ──────────────────────────────────────────────────────────
    crop_rows = (
        db.query(models.SoilRecord.crop_prediction)
        .filter(models.SoilRecord.crop_prediction.isnot(None))
        .all()
    )
    crop_counts = Counter(row[0] for row in crop_rows)
    top_crop = crop_counts.most_common(1)[0][0] if crop_counts else None

    # ── Top fertilizer ────────────────────────────────────────────────────
    fert_rows = (
        db.query(models.SoilRecord.fertilizer_prediction)
        .filter(models.SoilRecord.fertilizer_prediction.isnot(None))
        .all()
    )
    fert_counts = Counter(row[0] for row in fert_rows)
    top_fertilizer = fert_counts.most_common(1)[0][0] if fert_counts else None

    logger.info(
        "Dashboard stats | images=%s farms=%s predictions=%s top_crop=%s top_fertilizer=%s",
        total_images, total_farms, total_predictions, top_crop, top_fertilizer,
    )

    return schemas.DashboardOut(
        total_images=total_images,
        total_farms=total_farms,
        total_predictions=total_predictions,
        top_crop=top_crop,
        top_fertilizer=top_fertilizer,
    )
