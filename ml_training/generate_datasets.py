"""
ml_training/generate_datasets.py
-----------------------
Generates realistic sample CSV datasets for training.
Run this ONLY if you don't have real datasets yet.

Real datasets from Kaggle:
  - Crop: https://www.kaggle.com/data/atharvaingle/crop-recommendation-dataset
  - Fertilizer: https://www.kaggle.com/data/gdabhishek/fertilizer-prediction

Usage:
    python ml_training/generate_datasets.py
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
os.makedirs("data", exist_ok=True)

CROP_PROFILES = {
    "rice":       dict(N=(60,100), P=(40,60),  K=(35,50),  temp=(22,27), hum=(80,90), ph=(5.5,6.5), rain=(180,300)),
    "maize":      dict(N=(70,110), P=(50,70),  K=(40,60),  temp=(18,27), hum=(55,75), ph=(5.8,7.0), rain=(80,120)),
    "chickpea":   dict(N=(30,50),  P=(50,75),  K=(70,90),  temp=(15,25), hum=(15,30), ph=(6.0,7.5), rain=(60,100)),
    "kidneybeans":dict(N=(15,25),  P=(60,80),  K=(15,30),  temp=(15,25), hum=(18,25), ph=(6.0,7.0), rain=(80,120)),
    "pigeonpeas": dict(N=(15,25),  P=(55,70),  K=(15,25),  temp=(20,27), hum=(40,65), ph=(5.5,7.0), rain=(60,100)),
    "mungbean":   dict(N=(15,30),  P=(45,65),  K=(15,25),  temp=(25,35), hum=(50,70), ph=(6.2,7.2), rain=(60,100)),
    "blackgram":  dict(N=(30,50),  P=(55,75),  K=(15,25),  temp=(25,35), hum=(60,75), ph=(5.5,7.0), rain=(60,100)),
    "lentil":     dict(N=(15,25),  P=(65,80),  K=(15,25),  temp=(15,25), hum=(40,60), ph=(6.0,7.5), rain=(40,80)),
    "pomegranate":dict(N=(10,20),  P=(10,20),  K=(40,50),  temp=(25,35), hum=(85,95), ph=(5.5,7.0), rain=(100,180)),
    "banana":     dict(N=(80,120), P=(70,90),  K=(45,55),  temp=(25,35), hum=(75,90), ph=(5.5,6.5), rain=(100,170)),
    "mango":      dict(N=(15,25),  P=(15,25),  K=(15,25),  temp=(24,35), hum=(50,70), ph=(5.5,7.5), rain=(90,120)),
    "grapes":     dict(N=(10,25),  P=(100,140),K=(195,210),temp=(8,20),  hum=(80,90), ph=(5.5,6.5), rain=(60,100)),
    "watermelon": dict(N=(90,120), P=(10,20),  K=(40,50),  temp=(25,35), hum=(85,95), ph=(5.5,7.0), rain=(40,80)),
    "muskmelon":  dict(N=(90,120), P=(10,20),  K=(40,50),  temp=(28,38), hum=(90,95), ph=(5.5,7.0), rain=(20,40)),
    "apple":      dict(N=(0,10),   P=(100,140),K=(195,210),temp=(20,25), hum=(90,95), ph=(5.5,6.5), rain=(100,130)),
    "orange":     dict(N=(0,10),   P=(5,15),   K=(5,15),   temp=(10,20), hum=(90,95), ph=(6.0,7.5), rain=(110,140)),
    "papaya":     dict(N=(40,55),  P=(35,50),  K=(45,55),  temp=(25,35), hum=(90,95), ph=(6.0,7.0), rain=(130,170)),
    "coconut":    dict(N=(5,15),   P=(5,15),   K=(35,45),  temp=(25,32), hum=(90,95), ph=(5.0,8.0), rain=(130,170)),
    "cotton":     dict(N=(115,135),P=(40,55),  K=(15,25),  temp=(21,27), hum=(65,75), ph=(6.0,7.0), rain=(75,115)),
    "jute":       dict(N=(60,90),  P=(40,55),  K=(35,45),  temp=(24,35), hum=(70,90), ph=(6.0,7.0), rain=(170,220)),
    "coffee":     dict(N=(95,115), P=(27,35),  K=(27,35),  temp=(22,28), hum=(55,70), ph=(6.0,6.8), rain=(150,220)),
    "wheat":      dict(N=(100,140),P=(40,60),  K=(35,50),  temp=(15,25), hum=(60,75), ph=(6.0,7.0), rain=(65,105)),
}

SAMPLES_PER_CLASS = 100
rows = []

for crop, p in CROP_PROFILES.items():
    n = np.random.uniform(*p["N"],    SAMPLES_PER_CLASS)
    ph_vals = np.random.uniform(*p["P"],  SAMPLES_PER_CLASS)
    k = np.random.uniform(*p["K"],    SAMPLES_PER_CLASS)
    t = np.random.uniform(*p["temp"], SAMPLES_PER_CLASS)
    h = np.random.uniform(*p["hum"],  SAMPLES_PER_CLASS)
    ph = np.random.uniform(*p["ph"],  SAMPLES_PER_CLASS)
    r = np.random.uniform(*p["rain"], SAMPLES_PER_CLASS)
    for i in range(SAMPLES_PER_CLASS):
        rows.append({
            "N": round(n[i], 2),
            "P": round(ph_vals[i], 2),
            "K": round(k[i], 2),
            "temperature": round(t[i], 2),
            "humidity": round(h[i], 2),
            "ph": round(ph[i], 2),
            "rainfall": round(r[i], 2),
            "label": crop,
        })

crop_df = pd.DataFrame(rows)
crop_df = crop_df.sample(frac=1, random_state=42).reset_index(drop=True)
crop_df.to_csv("data/Crop_recommendation.csv", index=False)
print(f"Crop dataset saved: {len(crop_df)} rows, {crop_df['label'].nunique()} classes")

SOIL_TYPES  = ["Sandy", "Loamy", "Black", "Red", "Clayey"]
CROP_TYPES  = ["Maize", "Sugarcane", "Cotton", "Tobacco", "Paddy",
               "Barley", "Wheat", "Millets", "Oil seeds", "Pulses", "Ground Nuts"]
FERTILIZERS = ["Urea", "DAP", "14-35-14", "28-28", "17-17-17", "20-20", "10-26-26"]

def assign_fertilizer(n, p, k):
    """Choose fertilizer based on nutrient deficiency."""
    if n < 20 and p < 20:
        return "DAP"
    elif n < 20:
        return "Urea"
    elif p < 20 and k < 20:
        return "10-26-26"
    elif n > 35 and p > 35:
        return "17-17-17"
    elif p > 35:
        return "14-35-14"
    elif k < 20:
        return "28-28"
    else:
        return "20-20"

FERT_SAMPLES = 1500
fert_rows = []
for _ in range(FERT_SAMPLES):
    temp    = round(np.random.uniform(15, 40), 2)
    humidity= round(np.random.uniform(20, 90), 2)
    moisture= round(np.random.uniform(10, 80), 2)
    soil    = np.random.choice(SOIL_TYPES)
    crop    = np.random.choice(CROP_TYPES)
    n_val   = round(np.random.uniform(5, 50), 2)
    k_val   = round(np.random.uniform(5, 50), 2)
    p_val   = round(np.random.uniform(5, 50), 2)
    fert    = assign_fertilizer(n_val, p_val, k_val)
    fert_rows.append({
        "Temperature":   temp,
        "Humidity":      humidity,
        "Moisture":      moisture,
        "Soil Type":     soil,
        "Crop Type":     crop,
        "Nitrogen":      n_val,
        "Potassium":     k_val,
        "Phosphorous":   p_val,
        "Fertilizer Name": fert,
    })

fert_df = pd.DataFrame(fert_rows)
fert_df.to_csv("data/fertilizer_recommendation.csv", index=False)
print(f"Fertilizer dataset saved: {len(fert_df)} rows")
