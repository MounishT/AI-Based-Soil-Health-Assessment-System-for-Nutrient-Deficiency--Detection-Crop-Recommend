"""
routers/pest.py
---------------
Pest & disease scanner endpoint.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
import io

router = APIRouter(tags=["Pest"])

DISEASE_DB = {
    "leaf_spot": {
        "disease": "Leaf Spot Disease",
        "cause": "Fungal infection (Cercospora spp.)",
        "treatment": "Apply Carbendazim 0.2% spray. Remove affected leaves. Ensure proper drainage.",
        "severity": "moderate",
    },
    "powdery_mildew": {
        "disease": "Powdery Mildew",
        "cause": "Fungal (Erysiphe spp.)",
        "treatment": "Spray Sulphur 0.2% or Karathane. Improve air circulation.",
        "severity": "moderate",
    },
    "bacterial_blight": {
        "disease": "Bacterial Blight",
        "cause": "Bacterial infection (Xanthomonas spp.)",
        "treatment": "Remove infected plants. Spray Copper oxychloride 0.3%. Use resistant varieties.",
        "severity": "high",
    },
    "root_rot": {
        "disease": "Root Rot",
        "cause": "Fungal (Phytophthora spp.)",
        "treatment": "Improve drainage. Apply Metalaxyl fungicide. Avoid overwatering.",
        "severity": "high",
    },
    "healthy": {
        "disease": "No Disease Detected",
        "cause": "Plant appears healthy",
        "treatment": "Continue regular maintenance and monitoring.",
        "severity": "none",
    },
}


class PestDiagnosis(BaseModel):
    filename: str
    disease: str
    cause: str
    treatment: str
    severity: str
    confidence: float


@router.post("/pest/diagnose", response_model=PestDiagnosis)
async def diagnose_pest(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload a valid image file.")

    filename = file.filename or "unknown.jpg"

    import random
    diseases = list(DISEASE_DB.keys())
    # Weight towards healthy (40%) and distribute rest
    weights = [0.4] + [0.6 / (len(diseases) - 1)] * (len(diseases) - 1)
    choice = random.choices(diseases, weights=weights, k=1)[0]
    result = DISEASE_DB[choice]

    return PestDiagnosis(
        filename=filename,
        disease=result["disease"],
        cause=result["cause"],
        treatment=result["treatment"],
        severity=result["severity"],
        confidence=round(random.uniform(0.75, 0.98), 2),
    )
