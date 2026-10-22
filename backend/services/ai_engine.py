import joblib
import os
import numpy as np
from backend.config import settings

# Load existing Random Forest Models for Smart Decision Engine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CROP_MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "models", "crop_model.pkl")
FERT_MODEL_PATH = os.path.join(BASE_DIR, "..", "..", "models", "fertilizer_model.pkl")

# We use the models defensively in case they haven't been generated
try:
    crop_model = joblib.load(CROP_MODEL_PATH)
    fert_model = joblib.load(FERT_MODEL_PATH)
except Exception as e:
    print(f"Warning: Could not load traditional ML models. Run train scripts first. Error: {e}")
    crop_model = None
    fert_model = None

def get_anti_gravity_treatment_plan(cnn_deficiency_prediction: str, n: float, p: float, k: float, temp: float):
    """
    Combines the CNN Image Output with the Soil Data to create a holistic treatment plan.
    This is the core of the "AI" predictive engine.
    """
    # 1. Map CNN prediction to nutrient urgency
    urgency = "Normal"
    if "Deficiency" in cnn_deficiency_prediction:
        urgency = "High (Immediate Action Required)"
    
    # 2. Estimate Recovery Time (Simulation metric for dashboard)
    # The more severe the NPK lack, the longer the recovery.
    # Optimal NPK roughly ~50-100 depending on crop. 
    npk_avg = (n + p + k) / 3.0
    recovery_days = int(max(7, 30 - (npk_avg * 0.2)))
    if cnn_deficiency_prediction == "Healthy":
        recovery_days = 0
        urgency = "None"
        
    # 3. Base Fertilizer Recommendation (from existing ML model if available)
    # Dummy input format expected by fertilizer model: [Temparature, Humidity, Moisture, Soil Type, Crop Type, Nitrogen, Potassium, Phosphorous]
    # For this advanced endpoint, we'll provide a simplified smart suggestion if the full model isn't called directly.
    smart_fertilizer = "Balanced NPK 10-10-10"
    if cnn_deficiency_prediction == "Nitrogen_Deficiency":
        smart_fertilizer = "High-Nitrogen Fertilizer (e.g. Urea or Blood Meal)"
    elif cnn_deficiency_prediction == "Phosphorus_Deficiency":
        smart_fertilizer = "High-Phosphorus Fertilizer (e.g. Bone Meal)"
    elif cnn_deficiency_prediction == "Potassium_Deficiency":
        smart_fertilizer = "Potash-rich Fertilizer (e.g. Kelp Meal)"
        
    return {
        "status": cnn_deficiency_prediction,
        "urgency": urgency,
        "recommended_fertilizer": smart_fertilizer,
        "estimated_recovery_days": recovery_days,
        "action_plan": f"Apply {smart_fertilizer} immediately. Monitor soil moisture. Expected visible improvement in {recovery_days} days."
    }
