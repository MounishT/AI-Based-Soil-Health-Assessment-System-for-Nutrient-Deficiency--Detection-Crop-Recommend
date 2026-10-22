from fastapi import APIRouter, HTTPException, Query, Path, Body, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import datetime
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import crud
from backend.models import SoilReport, User
from backend.deps import get_optional_current_user

from backend.ml import fusion, cnn, structured
from backend.ml import fertilizer_dosage, crop_ranking, trend_prediction

router = APIRouter(tags=["Analysis"])

class AnalyzeRequest(BaseModel):
    field_id: int
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    image_id: Optional[int] = None
    explain: bool = False
    fuse: bool = False
    persist: bool = False

@router.post("/analyze")
def analyze(
    req: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    # 1. Soil Type Classification (if image_id provided)
    soil_type_classification = None
    predicted_type = None
    cnn_confidence = 0.0
    
    if req.image_id:
        db_image = crud.get_image(db, req.image_id)
        if not db_image:
            raise HTTPException(status_code=404, detail=f"Image with id={req.image_id} not found.")
        
        img_path = db_image.filepath 
        soil_type_classification = cnn.classify(img_path)
        predicted_type = soil_type_classification["soil_type"]
        cnn_confidence = soil_type_classification["confidence"]

    # 2. Hybrid Fusion
    fusion_data = {}
    thresholds_used = None
    if req.fuse and predicted_type:
        fusion_data = fusion.fuse(
            predicted_type=predicted_type,
            cnn_confidence=cnn_confidence,
           n_val=req.nitrogen,
            p_val=req.phosphorus,
            k_val=req.potassium,
            is_uncertain=soil_type_classification.get("is_uncertain", False)
        )
        if fusion_data.get("applied"):
            thresholds_used = fusion_data.get("thresholds_used")
            
    # 3. Diagnosis and Explainability (SHAP)
    diagnosis, diagnosis_detail = structured.diagnose(
        n=req.nitrogen,
        p=req.phosphorus,
        k=req.potassium,
        ph=req.ph,
        explain=req.explain,
        thresholds_used=thresholds_used
    )
    
    # 4. Soil Health Score Deductions
    score = 100.0
    deductions = []
    for nut, stat in diagnosis.items():
        if stat == "low":
            score -= 15.0
            deductions.append(f"{nut} is low")
        elif stat == "high" or stat == "acidic" or stat == "alkaline":
            score -= 10.0
            deductions.append(f"{nut} is {stat}")
            
    health_band = "excellent" if score >= 80 else "good" if score >= 60 else "moderate" if score >= 40 else "poor"
    
    # 5. Degradation Risk Index
    # Mocking trend calculation for API completeness
    degradation_risk = {
        "index": 0.676 if score < 60 else 0.210,
        "band": "high" if score < 60 else "low"
    }
    
    # 6. Recommendation Modules
    fert_rec = fertilizer_dosage.recommend_fertilizer_dosage(diagnosis)
    crop_rec = crop_ranking.rank_crop_suitability(req.nitrogen, req.phosphorus, req.potassium, req.ph)
    trend = trend_prediction.predict_soil_trend(req.nitrogen, req.phosphorus, req.potassium)
    
    response = {
        "soil_health_score": max(0, score),
        "diagnosis": diagnosis,
        "degradation_risk": degradation_risk,
        "health_band": health_band,
        "diagnosis_detail": diagnosis_detail,
        "fertilizer_recommendation": fert_rec,
        "crop_ranking": crop_rec,
        "trend_prediction": trend,
        "model_agreement": True, # Mocked
        "imputed_features": {}, # Mocked
        "inputs_used": req.dict()
    }
    
    img_url_or_path = None
    if req.image_id:
        response["soil_type_classification"] = soil_type_classification
        if db_image:
            img_url_or_path = db_image.filepath
    if req.fuse:
        response["fusion"] = fusion_data
        
    # 7. Persist to History if Authenticated
    if current_user:
        new_report = SoilReport(
            user_id=current_user.id,
            nitrogen=req.nitrogen,
            phosphorus=req.phosphorus,
            potassium=req.potassium,
            ph=req.ph,
            score=max(0, score),
            health_status=health_band,
            recommendations=fert_rec,  # using fert_rec for now
            image_path=img_url_or_path,
            metadata_json={"crop_ranking": crop_rec, "trend_prediction": trend, "diagnosis": diagnosis}
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        response["history_id"] = new_report.id
        
    return response

@router.post("/classify-soil/{image_id}")
def classify_soil(image_id: int):
    img_path = f"uploads/{image_id}.jpg"
    return cnn.classify(img_path)

@router.post("/explain-image/{image_id}")
def explain_image(image_id: int):
    img_path = f"uploads/{image_id}.jpg"
    return cnn.explain(img_path)

@router.get("/models/info")
def models_info():
    return {
        "cnn_model": {
            "description": "ResNet-50 trained on 5 classes.",
            "accuracy": "unknown", # Based on specifications note 2
            "caveats": "Accuracy is unmeasured for the checkpoint currently serving. Evaluated on 4 classes previously."
        },
        "structured_model": {
            "description": "RandomForest/XGBoost for nutrient deficiency.",
            "reliability": "high",
            "caveats": "Re-learned threshold rule from data."
        },
        "fusion": {
            "description": "Confidence-gated late fusion for NPK threshold adjustments.",
            "caveats": "Fusion multipliers are EDITORIAL, not fitted from data."
        }
    }

@router.get("/analysis-results/{id}")
def get_analysis_result(id: int):
    return {"id": id, "status": "Not implemented for demo"}
    
@router.get("/analysis-results/by-field/{id}")
def get_analysis_by_field(id: int):
    return []
