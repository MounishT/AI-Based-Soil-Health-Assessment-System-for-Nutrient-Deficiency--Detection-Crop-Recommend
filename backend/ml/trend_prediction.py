import numpy as np
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import random

def predict_soil_trend(current_n: float, current_p: float, current_k: float) -> dict:
    """
    Predicts soil health trend over the next 6 months using Ridge Regression.
    Uses synthetic historical data centered around the current values to simulate
    a realistic trajectory for N, P, and K.
    """
    # 1. Generate synthetic historical data (last 12 months)
    # We assume nutrients generally deplete over time if unmanaged
    months_history = np.arange(-12, 0).reshape(-1, 1)
    
    # Generate noisy historical data
    def generate_history(current_val, slope, noise_level):
        # Val = current_val + slope * month + noise
        # Since month is negative, positive slope means it was higher in the past (depletion)
        vals = current_val + (slope * months_history.flatten()) + np.random.normal(0, noise_level, 12)
        return np.maximum(0, vals) # Ensure no negative nutrients

    # Assume N depletes fastest, K slowest
    hist_n = generate_history(current_n, slope=-2.0, noise_level=5.0)
    hist_p = generate_history(current_p, slope=-1.0, noise_level=3.0)
    hist_k = generate_history(current_k, slope=-0.5, noise_level=4.0)

    # 2. Train Ridge Regression Models
    scaler = StandardScaler()
    months_scaled = scaler.fit_transform(months_history)
    
    model_n = Ridge(alpha=1.0).fit(months_scaled, hist_n)
    model_p = Ridge(alpha=1.0).fit(months_scaled, hist_p)
    model_k = Ridge(alpha=1.0).fit(months_scaled, hist_k)

    # 3. Predict next 6 months
    months_future = np.arange(1, 7).reshape(-1, 1)
    future_scaled = scaler.transform(months_future)
    
    pred_n = np.maximum(0, model_n.predict(future_scaled))
    pred_p = np.maximum(0, model_p.predict(future_scaled))
    pred_k = np.maximum(0, model_k.predict(future_scaled))

    # 4. Format data for frontend charting (line chart)
    # Combine historical and predicted data for a comprehensive view
    labels = [f"Month -{12 - i}" for i in range(12)] + [f"Month +{i+1}" for i in range(6)]
    
    # Concatenate history and prediction
    n_series = list(hist_n) + list(pred_n)
    p_series = list(hist_p) + list(pred_p)
    k_series = list(hist_k) + list(pred_k)

    chart_data = {
        "labels": labels,
        "datasets": [
            {
                "label": "Nitrogen",
                "data": [round(float(val), 1) for val in n_series],
                "borderColor": "rgb(255, 99, 132)",
                "backgroundColor": "rgba(255, 99, 132, 0.5)"
            },
            {
                "label": "Phosphorus",
                "data": [round(float(val), 1) for val in p_series],
                "borderColor": "rgb(54, 162, 235)",
                "backgroundColor": "rgba(54, 162, 235, 0.5)"
            },
            {
                "label": "Potassium",
                "data": [round(float(val), 1) for val in k_series],
                "borderColor": "rgb(75, 192, 192)",
                "backgroundColor": "rgba(75, 192, 192, 0.5)"
            }
        ]
    }
    
    # Generate simple summary
    n_trend = "depleting rapidly" if pred_n[-1] < current_n - 10 else "stable"
    p_trend = "depleting moderately" if pred_p[-1] < current_p - 5 else "stable"
    k_trend = "depleting slowly" if pred_k[-1] < current_k - 5 else "stable"

    summary = f"Over the next 6 months, Nitrogen is projected to be {n_trend}, Phosphorus is {p_trend}, and Potassium is {k_trend} without intervention."

    return {
        "chart_data": chart_data,
        "summary": summary
    }

