def rank_crop_suitability(n: float, p: float, k: float, ph: float) -> list:
    """
    Ranks crop suitability based on current soil NPK and pH levels.
    Uses basic absolute difference scoring. Lower score is better.
    """
    # Ideal requirements for different crops
    crop_requirements = {
        "Rice": {"n": 100, "p": 40, "k": 40, "ph": 6.0},
        "Wheat": {"n": 120, "p": 60, "k": 40, "ph": 6.5},
        "Maize": {"n": 100, "p": 60, "k": 40, "ph": 6.5},
        "Cotton": {"n": 120, "p": 60, "k": 40, "ph": 7.0},
        "Sugarcane": {"n": 150, "p": 80, "k": 60, "ph": 6.5},
        "Groundnut": {"n": 20, "p": 40, "k": 20, "ph": 6.5},
        "Soybean": {"n": 20, "p": 60, "k": 40, "ph": 6.5},
        "Tomato": {"n": 100, "p": 60, "k": 60, "ph": 6.5},
        "Potato": {"n": 120, "p": 80, "k": 100, "ph": 6.0},
        "Onion": {"n": 120, "p": 60, "k": 80, "ph": 6.5}
    }

    scored_crops = []
    
    for crop, req in crop_requirements.items():
        # Calculate deviation penalty
        n_penalty = abs(n - req["n"]) * 0.4
        p_penalty = abs(p - req["p"]) * 0.3
        k_penalty = abs(k - req["k"]) * 0.2
        ph_penalty = abs(ph - req["ph"]) * 10  # pH differences are small but critical
        
        total_penalty = n_penalty + p_penalty + k_penalty + ph_penalty
        
        # Convert penalty to a suitability score (out of 100)
        # Assuming max reasonable penalty is around 100-150
        suitability_score = max(0, 100 - (total_penalty / 2))
        
        scored_crops.append({
            "crop": crop,
            "suitability_score": round(suitability_score, 1),
            "ideal_n": req["n"],
            "ideal_p": req["p"],
            "ideal_k": req["k"],
            "ideal_ph": req["ph"]
        })
        
    # Sort by highest score first
    scored_crops.sort(key=lambda x: x["suitability_score"], reverse=True)
    
    # Return top 3 crops
    return scored_crops[:3]
