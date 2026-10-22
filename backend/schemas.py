"""
schemas.py
----------
Pydantic v2 schemas for request validation and response serialisation
in the AI-Based Soil Health Assessment System.

Schema Naming Convention:
    <Model>Base    → shared fields (no id / timestamps)
    <Model>Create  → fields required for POST requests
    <Model>Update  → optional fields for PATCH requests
    <Model>Out     → full response (includes id + timestamps)
"""

from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict


# ══════════════════════════════════════════════════════════════════════════════
# IMAGE SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class ImageBase(BaseModel):
    """Shared image fields."""
    filename: str = Field(..., min_length=1, max_length=255, description="Original filename of the uploaded image")
    filepath: str = Field(..., min_length=1, max_length=512, description="Relative path where image is stored on disk")


class ImageCreate(ImageBase):
    """
    Schema used internally when saving a new image record.
    (Clients upload via multipart/form-data — not this schema directly.)
    """
    pass


class ImageOut(ImageBase):
    """Full image response returned to the client."""
    id: int = Field(..., description="Unique image identifier")
    uploaded_at: datetime = Field(..., description="UTC timestamp of upload")

    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════════════════════════════════════
# FARM SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class FarmBase(BaseModel):
    """Shared farm fields."""
    farmer_name: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Full name of the farmer",
        examples=["Ramesh Kumar"],
    )
    location: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Farm location (village / district / city)",
        examples=["Chittoor, Andhra Pradesh"],
    )


class FarmCreate(FarmBase):
    """Request body for POST /farms."""
    pass


class FarmUpdate(BaseModel):
    """Request body for PATCH /farms/{id} — all fields optional."""
    farmer_name: Optional[str] = Field(None, min_length=2, max_length=150)
    location: Optional[str] = Field(None, min_length=2, max_length=255)


class FarmOut(FarmBase):
    """Full farm response returned to the client."""
    id: int = Field(..., description="Unique farm identifier")
    created_at: datetime = Field(..., description="UTC timestamp of farm creation")

    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════════════════════════════════════
# SOIL RECORD SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class SoilRecordBase(BaseModel):
    """Shared soil record fields with validation ranges."""

    farm_id: int = Field(..., gt=0, description="ID of the associated farm")
    image_id: Optional[int] = Field(None, gt=0, description="ID of the associated soil image (optional)")

    # ── NPK Nutrients ─────────────────────────────────────────────────────
    nitrogen: float = Field(
        ..., ge=0, le=500,
        description="Nitrogen content in mg/kg",
        examples=[90],
        alias="N",
    )
    phosphorus: float = Field(
        ..., ge=0, le=500,
        description="Phosphorus content in mg/kg",
        examples=[42],
        alias="P",
    )
    potassium: float = Field(
        ..., ge=0, le=500,
        description="Potassium content in mg/kg",
        examples=[43],
        alias="K",
    )

    # ── Environmental ─────────────────────────────────────────────────────
    temperature: float = Field(
        ..., ge=-10, le=60,
        description="Temperature in Celsius",
        examples=[25.5],
    )
    humidity: float = Field(
        ..., ge=0, le=100,
        description="Relative humidity percentage",
        examples=[80.0],
    )
    ph: float = Field(
        ..., ge=0, le=14,
        description="Soil pH value",
        examples=[6.5],
    )
    rainfall: float = Field(
        ..., ge=0, le=5000,
        description="Rainfall in mm",
        examples=[202.0],
    )
    moisture: Optional[float] = Field(
        None, ge=0, le=100,
        description="Soil moisture percentage",
        examples=[60.0],
    )

    # ── Classification ────────────────────────────────────────────────────
    soil_type: Optional[str] = Field(
        None,
        max_length=100,
        description="Soil type (e.g., Clay, Sandy, Loam, Red, Black)",
        examples=["Clay"],
    )
    crop_type: Optional[str] = Field(
        None,
        max_length=100,
        description="Current or intended crop type (used for fertilizer prediction)",
        examples=["Rice"],
    )

    notes: Optional[str] = Field(None, max_length=1000, description="Optional field notes")

    # ── Allow both 'N' alias and 'nitrogen' field name ────────────────────
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,   # accept both alias ('N') and field name ('nitrogen')
    )

    # ── Validators ────────────────────────────────────────────────────────
    @field_validator("soil_type")
    @classmethod
    def validate_soil_type(cls, v: Optional[str]) -> Optional[str]:
        """Normalise and validate soil type values."""
        if v is None:
            return v
        allowed = {"Clay", "Sandy", "Loam", "Red", "Black", "Silty", "Peaty", "Chalky"}
        normalised = v.strip().title()
        if normalised not in allowed:
            raise ValueError(
                f"Invalid soil_type '{v}'. "
                f"Allowed values: {', '.join(sorted(allowed))}"
            )
        return normalised

    @field_validator("ph")
    @classmethod
    def validate_ph(cls, v: float) -> float:
        """Round pH to 2 decimal places."""
        return round(v, 2)


class SoilRecordCreate(SoilRecordBase):
    """Request body for POST /soil-records."""
    pass


class SoilRecordUpdate(BaseModel):
    """Request body for PATCH /soil-records/{id} — all fields optional."""
    nitrogen: Optional[float] = Field(None, ge=0, le=500, alias="N")
    phosphorus: Optional[float] = Field(None, ge=0, le=500, alias="P")
    potassium: Optional[float] = Field(None, ge=0, le=500, alias="K")
    temperature: Optional[float] = Field(None, ge=-10, le=60)
    humidity: Optional[float] = Field(None, ge=0, le=100)
    ph: Optional[float] = Field(None, ge=0, le=14)
    rainfall: Optional[float] = Field(None, ge=0, le=5000)
    moisture: Optional[float] = Field(None, ge=0, le=100)
    soil_type: Optional[str] = Field(None, max_length=100)
    crop_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = Field(None, max_length=1000)

    model_config = ConfigDict(populate_by_name=True)


class SoilRecordOut(BaseModel):
    """Full soil record response returned to the client."""
    id: int
    farm_id: int
    image_id: Optional[int] = None
    nitrogen: float = Field(serialization_alias="N")
    phosphorus: float = Field(serialization_alias="P")
    potassium: float = Field(serialization_alias="K")
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    moisture: Optional[float] = None
    soil_type: Optional[str] = None
    crop_type: Optional[str] = None
    crop_prediction: Optional[str] = None
    fertilizer_prediction: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# ══════════════════════════════════════════════════════════════════════════════
# PREDICTION SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class CropPredictionRequest(BaseModel):
    """
    Input for POST /predict/crop.
    Features required by the RandomForestClassifier crop model.
    """
    N: float = Field(..., ge=0, le=500, description="Nitrogen (mg/kg)", examples=[90])
    P: float = Field(..., ge=0, le=500, description="Phosphorus (mg/kg)", examples=[42])
    K: float = Field(..., ge=0, le=500, description="Potassium (mg/kg)", examples=[43])
    temperature: float = Field(..., ge=-10, le=60, description="Temperature (°C)", examples=[25.5])
    humidity: float = Field(..., ge=0, le=100, description="Humidity (%)", examples=[80.0])
    ph: float = Field(..., ge=0, le=14, description="Soil pH", examples=[6.5])
    rainfall: float = Field(..., ge=0, le=5000, description="Rainfall (mm)", examples=[202.0])


class CropPredictionResponse(BaseModel):
    """Response from the crop prediction endpoint."""
    prediction: str = Field(..., description="Recommended crop name", examples=["Rice"])
    confidence: Optional[float] = Field(
        None, description="Model confidence score (0.0 – 1.0)", examples=[0.95]
    )


class FertilizerPredictionRequest(BaseModel):
    """
    Input for POST /predict/fertilizer.
    Features required by the RandomForestClassifier fertilizer model.
    """
    temperature: float = Field(..., ge=-10, le=60, examples=[25.0])
    humidity: float = Field(..., ge=0, le=100, examples=[80.0])
    moisture: float = Field(..., ge=0, le=100, examples=[60.0])
    soil_type: str = Field(..., examples=["Clay"])
    crop_type: str = Field(..., examples=["Rice"])
    N: float = Field(..., ge=0, le=500, description="Nitrogen (mg/kg)", examples=[90])
    P: float = Field(..., ge=0, le=500, description="Phosphorus (mg/kg)", examples=[42])
    K: float = Field(..., ge=0, le=500, description="Potassium (mg/kg)", examples=[43])

    @field_validator("soil_type")
    @classmethod
    def validate_soil_type(cls, v: str) -> str:
        allowed = {"Clay", "Sandy", "Loam", "Red", "Black", "Silty", "Peaty", "Chalky"}
        normalised = v.strip().title()
        if normalised not in allowed:
            raise ValueError(f"Invalid soil_type. Allowed: {', '.join(sorted(allowed))}")
        return normalised


class FertilizerPredictionResponse(BaseModel):
    """Response from the fertilizer prediction endpoint."""
    prediction: str = Field(..., description="Recommended fertilizer name", examples=["Urea"])
    confidence: Optional[float] = Field(
        None, description="Model confidence score (0.0 – 1.0)", examples=[0.92]
    )


# ══════════════════════════════════════════════════════════════════════════════
# HISTORY SCHEMA
# ══════════════════════════════════════════════════════════════════════════════

class PredictionHistoryOut(BaseModel):
    """Single entry in the prediction history response."""
    record_id: int = Field(..., description="Soil record ID")
    image: Optional[str] = Field(None, description="Image filename")
    farm: Optional[str] = Field(None, description="Farmer name")
    crop: Optional[str] = Field(None, description="Predicted crop")
    fertilizer: Optional[str] = Field(None, description="Predicted fertilizer")
    date: datetime = Field(..., description="Record creation timestamp")

    model_config = ConfigDict(from_attributes=True)


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD SCHEMA
# ══════════════════════════════════════════════════════════════════════════════

class DashboardOut(BaseModel):
    """Aggregated statistics for the dashboard endpoint."""
    total_images: int = Field(..., description="Total number of uploaded images")
    total_farms: int = Field(..., description="Total number of registered farms")
    total_predictions: int = Field(..., description="Total number of soil records with predictions")
    top_crop: Optional[str] = Field(None, description="Most frequently predicted crop")
    top_fertilizer: Optional[str] = Field(None, description="Most frequently predicted fertilizer")


# ══════════════════════════════════════════════════════════════════════════════
# GENERIC RESPONSE SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class MessageResponse(BaseModel):
    """Generic success/info message response."""
    message: str = Field(..., examples=["Operation completed successfully."])


class ErrorResponse(BaseModel):
    """Standard error response body."""
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Machine-readable error code")

# ------------------------------------------------------------------------------
# CNN / ANTI-GRAVITY SCHEMAS
# ------------------------------------------------------------------------------

class AntiGravityPlan(BaseModel):
    status: str
    urgency: str
    recommended_fertilizer: str
    estimated_recovery_days: int
    action_plan: str

class CNNDiagnosisResponse(BaseModel):
    filename: str
    filepath: str
    heatmap_url: Optional[str] = None
    cnn_prediction: str
    anti_gravity_plan: AntiGravityPlan


# ══════════════════════════════════════════════════════════════════════════════
# AUTH SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class UserRegister(BaseModel):
    """Request body for POST /auth/register."""
    email: str = Field(..., description="User email address", examples=["user@example.com"])
    password: str = Field(..., min_length=6, max_length=128, description="Plain text password")
    full_name: Optional[str] = Field(None, max_length=150, description="Optional display name")


class UserLogin(BaseModel):
    """Request body for POST /auth/login."""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="Plain text password")


class UserOut(BaseModel):
    """User response returned to the client (no password)."""
    id: int = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, description="Display name")
    is_active: bool = Field(..., description="Whether the account is active")
    created_at: datetime = Field(..., description="UTC timestamp of account creation")

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """JWT token response returned after successful login."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserOut = Field(..., description="Authenticated user info")

# ══════════════════════════════════════════════════════════════════════════════
# HISTORY / SOIL REPORT SCHEMAS
# ══════════════════════════════════════════════════════════════════════════════

class SoilReportResponse(BaseModel):
    id: int
    user_id: int
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    score: Optional[float] = None
    health_status: Optional[str] = None
    recommendations: Optional[Any] = None
    image_path: Optional[str] = None
    metadata_json: Optional[Any] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PaginatedHistoryResponse(BaseModel):
    items: list[SoilReportResponse]
    total: int
