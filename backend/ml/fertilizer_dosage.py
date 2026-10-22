def recommend_fertilizer_dosage(diagnosis: dict) -> list:
    """
    Rule-based logic to map deficiencies to specific fertilizer types,
    dosages (kg/acre), and application schedules.
    """
    recommendations = []

    # Nitrogen Rules
    if diagnosis.get("nitrogen") == "low":
        recommendations.append({
            "nutrient": "Nitrogen",
            "fertilizer_type": "Urea (46% N)",
            "dosage_kg_per_acre": "20-30",
            "schedule": "Split into 2-3 doses (basal and top dressing at active tillering)"
        })
    elif diagnosis.get("nitrogen") == "high":
        recommendations.append({
            "nutrient": "Nitrogen",
            "fertilizer_type": "None",
            "dosage_kg_per_acre": "0",
            "schedule": "Avoid nitrogenous fertilizers to prevent excessive vegetative growth."
        })

    # Phosphorus Rules
    if diagnosis.get("phosphorus") == "low":
        recommendations.append({
            "nutrient": "Phosphorus",
            "fertilizer_type": "Single Super Phosphate (SSP - 16% P2O5) or DAP",
            "dosage_kg_per_acre": "15-25",
            "schedule": "Apply full dose as basal application before sowing."
        })

    # Potassium Rules
    if diagnosis.get("potassium") == "low":
        recommendations.append({
            "nutrient": "Potassium",
            "fertilizer_type": "Muriate of Potash (MOP - 60% K2O)",
            "dosage_kg_per_acre": "10-20",
            "schedule": "Apply as basal dose. Can be split for sandy soils."
        })

    # pH Rules
    if diagnosis.get("ph") == "acidic":
        recommendations.append({
            "nutrient": "pH",
            "fertilizer_type": "Agricultural Lime",
            "dosage_kg_per_acre": "100-200",
            "schedule": "Incorporate into soil 2-4 weeks before sowing."
        })
    elif diagnosis.get("ph") == "alkaline":
        recommendations.append({
            "nutrient": "pH",
            "fertilizer_type": "Gypsum or Elemental Sulfur",
            "dosage_kg_per_acre": "50-100",
            "schedule": "Apply and irrigate well before sowing."
        })

    return recommendations
