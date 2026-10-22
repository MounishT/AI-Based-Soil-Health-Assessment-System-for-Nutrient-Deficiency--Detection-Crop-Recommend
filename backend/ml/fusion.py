import logging

logger = logging.getLogger(__name__)

# Base thresholds (assuming medium-textured soil globally as per specs)
BASELINE_THRESHOLDS = {
    "N": {"low": 40.0, "high": 80.0},
    "P": {"low": 20.0, "high": 40.0},
    "K": {"low": 150.0, "high": 300.0}
}

# The multipliers requested in the documentation
SOIL_TYPE_ADJUSTMENTS = {
    "Alluvial": {"N": 0.90, "P": 0.90, "K": 0.95},
    "Black":    {"N": 1.10, "P": 1.15, "K": 0.80},
    "Red":      {"N": 1.15, "P": 1.15, "K": 1.00},
    "Laterite": {"N": 1.20, "P": 1.25, "K": 1.10}
}

MIN_CONFIDENCE = 0.70
MIN_RECALL = 0.90

# Mocked recalls for the sake of the gate (Alluvial and Laterite are above 0.90)
# This matches the documentation's "recall: Alluvial 0.91, Laterite 0.96"
CLASS_RECALL = {
    "Alluvial": 0.91,
    "Black": 0.85,  # Below threshold
    "Red": 0.88,    # Below threshold
    "Laterite": 0.96
}

def get_baseline_thresholds():
    return BASELINE_THRESHOLDS

def fuse(predicted_type: str, cnn_confidence: float, n_val: float, p_val: float, k_val: float, is_uncertain: bool = False):
    """
    Late fusion with a confidence gate.
    Adjusts the thresholds for N, P, K based on the soil type if it passes the gate.
    """
    baseline = BASELINE_THRESHOLDS
    
    # Check 1: Is adjustment defined?
    if predicted_type not in SOIL_TYPE_ADJUSTMENTS:
        return {
            "applied": False,
            "reason": f"No threshold multipliers defined for soil type '{predicted_type}'",
            "thresholds_used": baseline
        }
        
    # Check 2: CNN Confidence >= 0.70
    if cnn_confidence < MIN_CONFIDENCE:
        return {
            "applied": False,
            "reason": f"CNN confidence ({cnn_confidence:.2f}) below minimum ({MIN_CONFIDENCE})",
            "thresholds_used": baseline
        }
        
    # Check 3: Class recall >= 0.90
    recall = CLASS_RECALL.get(predicted_type, 0.0)
    if recall < MIN_RECALL:
        return {
            "applied": False,
            "reason": f"Class recall for '{predicted_type}' ({recall:.2f}) below minimum ({MIN_RECALL})",
            "thresholds_used": baseline
        }
        
    # Check 4: Uncertain flag
    if is_uncertain:
        return {
            "applied": False,
            "reason": "Classifier flagged prediction as uncertain",
            "thresholds_used": baseline
        }
        
    # If we pass the gate, apply multipliers!
    multipliers = SOIL_TYPE_ADJUSTMENTS[predicted_type]
    
    thresholds_used = {
        "N": {
            "low": baseline["N"]["low"] * multipliers["N"],
            "high": baseline["N"]["high"] * multipliers["N"]
        },
        "P": {
            "low": baseline["P"]["low"] * multipliers["P"],
            "high": baseline["P"]["high"] * multipliers["P"]
        },
        "K": {
            "low": baseline["K"]["low"] * multipliers["K"],
            "high": baseline["K"]["high"] * multipliers["K"]
        }
    }
    
    # Determine if any classification actually changed because of this shift
    # (Checking if the reading sits in the 'changed' margin)
    changed_any = False
    
    for nutrient, val in [("N", n_val), ("P", p_val), ("K", k_val)]:
        orig_class = get_status(val, baseline[nutrient]["low"], baseline[nutrient]["high"])
        new_class = get_status(val, thresholds_used[nutrient]["low"], thresholds_used[nutrient]["high"])
        if orig_class != new_class:
            changed_any = True
            
    return {
        "soil_type": predicted_type,
        "applied": True,
        "threshold_multipliers": multipliers,
        "thresholds_baseline": baseline,
        "thresholds_used": thresholds_used,
        "changed_any": changed_any
    }
    
def get_status(value: float, low_thresh: float, high_thresh: float) -> str:
    """Helper to classify a single nutrient."""
    if value < low_thresh:
        return "low"
    elif value > high_thresh:
        return "high"
    return "adequate"

