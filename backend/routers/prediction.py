"""
routers/prediction.py
---------------------
FastAPI router for ML prediction endpoints, history, and dashboard.

Endpoints:
    POST  /predict/crop         → Predict crop from soil readings
    POST  /predict/fertilizer   → Predict fertilizer from soil + crop info
    POST  /predict/full/{id}    → Run both predictions on an existing soil record
    GET   /history              → Get prediction history
    GET   /dashboard            → Get dashboard statistics
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db
from backend.services.crop_predictor import CropPredictor
from backend.services.fertilizer_predictor import FertilizerPredictor

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─── Lazy-loaded singleton predictors (loaded once on first use) ──────────────
_crop_predictor: CropPredictor | None = None
_fertilizer_predictor: FertilizerPredictor | None = None


def get_crop_predictor() -> CropPredictor:
    """Return (and lazily initialise) the singleton CropPredictor."""
    global _crop_predictor
    if _crop_predictor is None:
        _crop_predictor = CropPredictor()
    return _crop_predictor


def get_fertilizer_predictor() -> FertilizerPredictor:
    """Return (and lazily initialise) the singleton FertilizerPredictor."""
    global _fertilizer_predictor
    if _fertilizer_predictor is None:
        _fertilizer_predictor = FertilizerPredictor()
    return _fertilizer_predictor


# ─── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(
    tags=["Predictions & Dashboard"],
    responses={500: {"description": "Internal server error (model not loaded)"}},
)


# ─── POST /predict/crop ───────────────────────────────────────────────────────
@router.post(
    "/predict/crop",
    response_model=schemas.CropPredictionResponse,
    summary="Predict recommended crop",
    description=(
        "Use the trained RandomForestClassifier crop model to predict "
        "the most suitable crop based on soil NPK values and environmental factors."
    ),
)
def predict_crop(
    request: schemas.CropPredictionRequest,
    predictor: CropPredictor = Depends(get_crop_predictor),
) -> schemas.CropPredictionResponse:
    """
    Predict the recommended crop from soil readings.

    **Input features**: N, P, K, temperature, humidity, ph, rainfall
    """
    logger.info("POST /predict/crop | N=%s P=%s K=%s ph=%s", request.N, request.P, request.K, request.ph)
    try:
        result = predictor.predict(
            N=request.N,
            P=request.P,
            K=request.K,
            temperature=request.temperature,
            humidity=request.humidity,
            ph=request.ph,
            rainfall=request.rainfall,
        )
        return schemas.CropPredictionResponse(
            prediction=result["prediction"],
            confidence=result.get("confidence"),
        )
    except Exception as exc:
        logger.error("Crop prediction failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Crop prediction failed: {str(exc)}",
        )


# ─── POST /predict/fertilizer ─────────────────────────────────────────────────
@router.post(
    "/predict/fertilizer",
    response_model=schemas.FertilizerPredictionResponse,
    summary="Predict recommended fertilizer",
    description=(
        "Use the trained RandomForestClassifier fertilizer model to predict "
        "the best fertilizer based on soil conditions and crop type."
    ),
)
def predict_fertilizer(
    request: schemas.FertilizerPredictionRequest,
    predictor: FertilizerPredictor = Depends(get_fertilizer_predictor),
) -> schemas.FertilizerPredictionResponse:
    """
    Predict the recommended fertilizer.

    **Input features**: temperature, humidity, moisture, soil_type, crop_type, N, P, K
    """
    logger.info(
        "POST /predict/fertilizer | soil_type=%s crop_type=%s",
        request.soil_type, request.crop_type,
    )
    try:
        result = predictor.predict(
            temperature=request.temperature,
            humidity=request.humidity,
            moisture=request.moisture,
            soil_type=request.soil_type,
            crop_type=request.crop_type,
            N=request.N,
            P=request.P,
            K=request.K,
        )
        return schemas.FertilizerPredictionResponse(
            prediction=result["prediction"],
            confidence=result.get("confidence"),
        )
    except Exception as exc:
        logger.error("Fertilizer prediction failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fertilizer prediction failed: {str(exc)}",
        )


# ─── POST /predict/full/{record_id} ──────────────────────────────────────────
@router.post(
    "/predict/full/{record_id}",
    response_model=schemas.SoilRecordOut,
    summary="Run full prediction on an existing soil record",
    description=(
        "Load an existing soil record by ID, run both crop and fertilizer predictions, "
        "and save the results back to the database."
    ),
)
def predict_full(
    record_id: int,
    db: Session = Depends(get_db),
    crop_predictor: CropPredictor = Depends(get_crop_predictor),
    fertilizer_predictor: FertilizerPredictor = Depends(get_fertilizer_predictor),
) -> schemas.SoilRecordOut:
    """
    Run crop + fertilizer prediction on an existing soil record and persist results.
    """
    logger.info("POST /predict/full/%s", record_id)

    # ── Load soil record ──────────────────────────────────────────────────
    record = crud.get_soil_record(db=db, record_id=record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Soil record with id={record_id} not found.",
        )

    # ── Crop prediction ───────────────────────────────────────────────────
    try:
        crop_result = crop_predictor.predict(
            N=record.nitrogen,
            P=record.phosphorus,
            K=record.potassium,
            temperature=record.temperature,
            humidity=record.humidity,
            ph=record.ph,
            rainfall=record.rainfall,
        )
        crop_prediction = crop_result["prediction"]
    except Exception as exc:
        logger.error("Crop prediction failed for record %s: %s", record_id, exc)
        crop_prediction = None

    # ── Fertilizer prediction ─────────────────────────────────────────────
    fertilizer_prediction = None
    if record.soil_type and record.crop_type:
        try:
            fert_result = fertilizer_predictor.predict(
                temperature=record.temperature,
                humidity=record.humidity,
                moisture=record.moisture or 50.0,
                soil_type=record.soil_type,
                crop_type=record.crop_type,
                N=record.nitrogen,
                P=record.phosphorus,
                K=record.potassium,
            )
            fertilizer_prediction = fert_result["prediction"]
        except Exception as exc:
            logger.error("Fertilizer prediction failed for record %s: %s", record_id, exc)
    else:
        logger.warning(
            "Skipping fertilizer prediction for record %s — soil_type or crop_type missing.",
            record_id,
        )

    # ── Persist predictions ───────────────────────────────────────────────
    updated = crud.update_soil_record_predictions(
        db=db,
        record_id=record_id,
        crop_prediction=crop_prediction,
        fertilizer_prediction=fertilizer_prediction,
    )

    logger.info(
        "Full prediction complete | record_id=%s crop=%s fertilizer=%s",
        record_id, crop_prediction, fertilizer_prediction,
    )
    return updated


# ─── GET /history ─────────────────────────────────────────────────────────────
@router.get(
    "/history",
    response_model=List[schemas.PredictionHistoryOut],
    summary="Get prediction history",
    description="Retrieve all soil records that have at least one ML prediction, newest first.",
)
def get_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> List[schemas.PredictionHistoryOut]:
    """Return the full prediction history with image, farm, crop, and fertilizer info."""
    logger.info("GET /history | skip=%s limit=%s", skip, limit)
    history = crud.get_prediction_history(db=db, skip=skip, limit=limit)
    return [schemas.PredictionHistoryOut(**h) for h in history]


# ─── GET /dashboard ───────────────────────────────────────────────────────────
@router.get(
    "/dashboard",
    response_model=schemas.DashboardOut,
    summary="Get dashboard statistics",
    description=(
        "Return aggregated counts and top predictions for the admin dashboard: "
        "total images, farms, predictions, most common crop, and most common fertilizer."
    ),
)
def get_dashboard(
    db: Session = Depends(get_db),
) -> schemas.DashboardOut:
    """Aggregate and return system-wide statistics."""
    logger.info("GET /dashboard")
    return crud.get_dashboard_stats(db=db)
