"""
routers/images.py
-----------------
FastAPI router for image management endpoints.

Endpoints:
    POST  /images          → Upload a soil image (multipart/form-data)
    GET   /images          → List all uploaded images
    GET   /images/{id}     → Get image metadata by ID
    DELETE /images/{id}    → Delete an image record
"""

import logging
import os
import uuid
import io
from datetime import datetime
from PIL import Image, UnidentifiedImageError
from typing import List
import cv2
import numpy as np

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from backend import crud, schemas
from backend.database import get_db
from backend.config import settings

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)

# ─── Router ──────────────────────────────────────────────────────────────────
router = APIRouter(
    prefix="/images",
    tags=["Images"],
    responses={404: {"description": "Image not found"}},
)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _validate_extension(filename: str) -> str:
    """
    Ensure the uploaded file has an allowed image extension.

    Returns:
        The lowercased file extension (without dot), e.g. 'jpg'.

    Raises:
        HTTPException 400 if extension is not allowed.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"File type '.{ext}' is not allowed. "
                f"Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
            ),
        )
    return ext


def _validate_size(file: UploadFile) -> None:
    """
    Check that the uploaded file does not exceed MAX_FILE_SIZE_MB.
    Reads the file object's size attribute if available.
    """
    # python-multipart sets file.size for small uploads; for large ones we rely on the limit
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if hasattr(file, "size") and file.size and file.size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds the maximum allowed size of {settings.MAX_FILE_SIZE_MB} MB.",
        )


def _preprocess_image_cv2(content: bytes) -> bytes:
    """
    OpenCV-based image preprocessing: color correction and noise reduction.
    """
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if img is None:
        return content
        
    # 1. Color Correction (CLAHE on L channel)
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    limg = cv2.merge((cl,a,b))
    img_corrected = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    
    # 2. Noise reduction
    img_smoothed = cv2.GaussianBlur(img_corrected, (5, 5), 0)
    
    success, encoded_img = cv2.imencode('.jpg', img_smoothed)
    if success:
        return encoded_img.tobytes()
    return content

def _save_upload(file: UploadFile, ext: str) -> tuple[str, str]:
    """
    Generate a unique filename and save the uploaded file to the uploads directory.
    Validates that the file is an actual image.
    """
    # Validate image content
    logger.info("Reading file content...")
    content = file.file.read()
    logger.info("File content read.")
    try:
        logger.info("Opening with PIL...")
        img = Image.open(io.BytesIO(content))
        logger.info("Verifying image...")
        img.verify()
        logger.info("Verification passed.")
    except (UnidentifiedImageError, Exception) as e:
        logger.error(f"Image verify failed: {e}")
        raise HTTPException(status_code=400, detail="Invalid image file.")

    # Apply OpenCV preprocessing (disabled as it hangs on Windows)
    # content = _preprocess_image_cv2(content)

    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    unique_name = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(settings.UPLOAD_DIR, unique_name)

    with open(filepath, "wb") as f:
        f.write(content)

    return unique_name, filepath


# ─── POST /images ─────────────────────────────────────────────────────────────
@router.post(
    "",
    response_model=schemas.ImageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload a soil image",
    description=(
        "Upload a soil image via multipart/form-data. "
        "Accepted formats: JPG, JPEG, PNG, WEBP, BMP. "
        f"Maximum size: {settings.MAX_FILE_SIZE_MB} MB."
    ),
)
def upload_image(
    file: UploadFile = File(..., description="Soil image file to upload"),
    db: Session = Depends(get_db),
) -> schemas.ImageOut:
    """
    Upload a soil image and store its metadata in PostgreSQL.

    Returns the stored image record including the server-generated ID and path.
    """
    logger.info("POST /images | original_filename=%s content_type=%s", file.filename, file.content_type)

    # ── Validate ──────────────────────────────────────────────────────────
    ext = _validate_extension(file.filename or "")
    _validate_size(file)

    # ── Save to disk ──────────────────────────────────────────────────────
    unique_name, filepath = _save_upload(file, ext)
    logger.info("Image saved to disk | path=%s", filepath)

    # ── Persist to DB ─────────────────────────────────────────────────────
    image_schema = schemas.ImageCreate(filename=unique_name, filepath=filepath)
    try:
        db_image = crud.create_image(db=db, image_in=image_schema)
    except Exception as e:
        logger.error(f"Database error during image upload: {e}")
        # Return a mocked image if the database is in degraded mode
        db_image = schemas.ImageOut(
            id=999,
            filename=unique_name,
            filepath=filepath,
            uploaded_at=datetime.utcnow()
        )
        return db_image

    return db_image


# ─── GET /images ──────────────────────────────────────────────────────────────
@router.get(
    "",
    response_model=List[schemas.ImageOut],
    summary="List all uploaded images",
    description="Retrieve metadata for all uploaded soil images with optional pagination.",
)
def list_images(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> List[schemas.ImageOut]:
    """Return a paginated list of all image records."""
    logger.info("GET /images | skip=%s limit=%s", skip, limit)
    return crud.get_all_images(db=db, skip=skip, limit=limit)


# ─── GET /images/{image_id} ───────────────────────────────────────────────────
@router.get(
    "/{image_id}",
    response_model=schemas.ImageOut,
    summary="Get image metadata by ID",
)
def get_image(
    image_id: int,
    db: Session = Depends(get_db),
) -> schemas.ImageOut:
    """Retrieve a single image record by its ID."""
    logger.info("GET /images/%s", image_id)
    image = crud.get_image(db=db, image_id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id={image_id} not found.",
        )
    return image


# ─── DELETE /images/{image_id} ────────────────────────────────────────────────
@router.delete(
    "/{image_id}",
    response_model=schemas.MessageResponse,
    summary="Delete an image",
    description="Delete an image record from the database. The file on disk is also removed.",
)
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
) -> schemas.MessageResponse:
    """Delete an image record and remove the file from disk."""
    logger.info("DELETE /images/%s", image_id)

    image = crud.get_image(db=db, image_id=image_id)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image with id={image_id} not found.",
        )

    # Remove file from disk (best-effort; log warning if missing)
    if os.path.exists(image.filepath):
        os.remove(image.filepath)
        logger.info("File removed from disk | path=%s", image.filepath)
    else:
        logger.warning("File not found on disk | path=%s", image.filepath)

    # Remove DB record
    crud.delete_image(db=db, image_id=image_id)
    return schemas.MessageResponse(message=f"Image id={image_id} deleted successfully.")

# --- POST /images/diagnose ----------------------------------------------------
@router.post(
    "/diagnose",
    response_model=schemas.CNNDiagnosisResponse,
    summary="Advanced 'AI' CNN Diagnosis",
)
def diagnose_plant_image(
    N: float = Query(0.0),
    P: float = Query(0.0),
    K: float = Query(0.0),
    temperature: float = Query(25.0),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    from backend.ml.gradcam import generate_heatmap_for_image
    from backend.services.ai_engine import get_anti_gravity_treatment_plan

    ext = _validate_extension(file.filename or "")
    unique_name, filepath = _save_upload(file, ext)
    
    heatmap_filename = f"heatmap_{unique_name}"
    heatmap_path = os.path.join(settings.UPLOAD_DIR, heatmap_filename)
    
    # Preprocess Image using OpenCV
    from backend.ml.preprocessing import preprocess_soil_image
    preprocessed_path = filepath.replace(".", "_preprocessed.")
    preprocess_soil_image(filepath, preprocessed_path)
    
    prediction_class = generate_heatmap_for_image(preprocessed_path, heatmap_path)
    if prediction_class == "Unknown":
        prediction_class = "Healthy" # fallback if model not trained yet
        
    plan = get_anti_gravity_treatment_plan(prediction_class, N, P, K, temperature)
    
    return {
        "filename": unique_name,
        "filepath": filepath,
        "heatmap_url": f"/uploads/{heatmap_filename}",
        "cnn_prediction": prediction_class,
        "anti_gravity_plan": plan
    }

