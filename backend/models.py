"""
models.py
---------
SQLAlchemy ORM models for the AI-Based Soil Health Assessment System.

Tables:
    - Image        → stores uploaded soil images
    - Farm         → stores farm and farmer details
    - SoilRecord   → stores soil readings, ML predictions, and links to Image/Farm
"""

import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import relationship, Mapped, mapped_column

from backend.database import Base

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


# ─── 1. Image Model ───────────────────────────────────────────────────────────
class Image(Base):
    """
    Stores metadata for uploaded soil images.

    Columns:
        id          → auto-increment primary key
        filename    → original filename of the uploaded image
        filepath    → path on disk (e.g., 'uploads/soil.jpg')
        uploaded_at → UTC timestamp when the image was stored
    """

    __tablename__ = "images"
    __allow_unmapped__ = True   # allow mixed annotation styles

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512), nullable=False, unique=True)
    uploaded_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    # One Image → many SoilRecords
    soil_records = relationship(
        "SoilRecord",
        back_populates="image",
        cascade="all, delete-orphan",   # delete records when image is deleted
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Image id={self.id} filename={self.filename!r}>"


# ─── 2. Farm Model ────────────────────────────────────────────────────────────
class Farm(Base):
    """
    Stores farm and farmer information.

    Columns:
        id           → auto-increment primary key
        farmer_name  → name of the farmer
        location     → geographical location / village / district
        created_at   → UTC timestamp when the farm was registered
    """

    __tablename__ = "farms"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farmer_name = Column(String(150), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    # One Farm → many SoilRecords
    soil_records = relationship(
        "SoilRecord",
        back_populates="farm",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Farm id={self.id} farmer_name={self.farmer_name!r} location={self.location!r}>"


# ─── 3. SoilRecord Model ──────────────────────────────────────────────────────
class SoilRecord(Base):
    """
    Stores soil sensor readings, contextual data, and ML predictions.

    Foreign Keys:
        farm_id  → references farms.id
        image_id → references images.id (nullable — record may not have an image)

    Soil Nutrient Columns:
        nitrogen    (N) → mg/kg
        phosphorus  (P) → mg/kg
        potassium   (K) → mg/kg

    Environmental Columns:
        temperature → °C
        humidity    → %
        ph          → 0–14 scale
        rainfall    → mm
        moisture    → %

    Classification Columns:
        soil_type   → e.g., "Clay", "Sandy", "Loam"
        crop_type   → e.g., "Rice", "Wheat" (user-provided for fertilizer model)

    Prediction Columns:
        crop_prediction        → crop recommended by ML model
        fertilizer_prediction  → fertilizer recommended by ML model

    Audit:
        created_at → UTC timestamp of record creation
    """

    __tablename__ = "soil_records"
    __allow_unmapped__ = True

    # ── Primary Key ───────────────────────────────────────────────────────
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # ── Foreign Keys ──────────────────────────────────────────────────────
    farm_id = Column(
        Integer,
        ForeignKey("farms.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_id = Column(
        Integer,
        ForeignKey("images.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Soil Nutrients (NPK) ──────────────────────────────────────────────
    nitrogen = Column(Float, nullable=False, comment="Nitrogen content (mg/kg)")
    phosphorus = Column(Float, nullable=False, comment="Phosphorus content (mg/kg)")
    potassium = Column(Float, nullable=False, comment="Potassium content (mg/kg)")

    # ── Environmental Factors ─────────────────────────────────────────────
    temperature = Column(Float, nullable=False, comment="Temperature in Celsius")
    humidity = Column(Float, nullable=False, comment="Relative humidity (%)")
    ph = Column(Float, nullable=False, comment="Soil pH value (0-14)")
    rainfall = Column(Float, nullable=False, comment="Rainfall in mm")
    moisture = Column(Float, nullable=True, comment="Soil moisture (%)")

    # ── Classification ────────────────────────────────────────────────────
    soil_type = Column(String(100), nullable=True, comment="e.g., Clay, Sandy, Loam")
    crop_type = Column(
        String(100),
        nullable=True,
        comment="User-provided crop type for fertilizer prediction",
    )

    # ── ML Predictions ────────────────────────────────────────────────────
    crop_prediction = Column(
        String(150), nullable=True, comment="Crop predicted by the ML model"
    )
    fertilizer_prediction = Column(
        String(150), nullable=True, comment="Fertilizer predicted by the ML model"
    )

    # ── Notes ─────────────────────────────────────────────────────────────
    notes = Column(Text, nullable=True, comment="Optional field notes")

    # ── Audit ─────────────────────────────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    farm = relationship("Farm", back_populates="soil_records", lazy="select")
    image = relationship("Image", back_populates="soil_records", lazy="select")

    def __repr__(self) -> str:
        return (
            f"<SoilRecord id={self.id} farm_id={self.farm_id} "
            f"crop={self.crop_prediction!r} fertilizer={self.fertilizer_prediction!r}>"
        )


# ─── 4. User Model ──────────────────────────────────────────────────────────
class User(Base):
    """
    Stores user accounts for email-based authentication.

    Columns:
        id              → auto-increment primary key
        email           → unique email address
        hashed_password → bcrypt-hashed password
        full_name       → optional display name
        is_active       → whether the account is active
        created_at      → UTC timestamp of account creation
    """

    __tablename__ = "users"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    reports = relationship(
        "SoilReport",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


# ─── 5. SoilReport Model (History) ──────────────────────────────────────────
class SoilReport(Base):
    """
    Stores historical soil analysis reports for users.
    """
    __tablename__ = "soil_reports"
    __allow_unmapped__ = True

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    nitrogen = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    score = Column(Float, nullable=True)
    health_status = Column(String(32), nullable=True)
    recommendations = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    image_path = Column(Text, nullable=True)
    metadata_json = Column(JSON().with_variant(JSONB, 'postgresql'), nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user = relationship("User", back_populates="reports", lazy="select")

    def __repr__(self) -> str:
        return f"<SoilReport id={self.id} user_id={self.user_id}>"
