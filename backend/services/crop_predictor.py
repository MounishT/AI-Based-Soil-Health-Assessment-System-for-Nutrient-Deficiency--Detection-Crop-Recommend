"""
services/crop_predictor.py
--------------------------
Service class that loads the trained crop model and exposes a
predict() method used by the FastAPI prediction router.

The model is loaded ONCE at class instantiation and reused
for every subsequent prediction (no repeated disk I/O).
"""

import logging
import os
from typing import Any

import numpy as np
import joblib

from backend.config import settings

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


class CropPredictor:
    """
    Wrapper around the trained crop recommendation pipeline.

    Attributes:
        pipeline       : Trained sklearn Pipeline (StandardScaler + RFC)
        label_encoder  : LabelEncoder mapping integer outputs → crop names
        feature_cols   : Ordered list of feature names the model expects
    """

    def __init__(self, model_path: str | None = None):
        """
        Load the serialised model from disk.

        Args:
            model_path : Path to the .pkl file.
                         Defaults to settings.CROP_MODEL_PATH.

        Raises:
            FileNotFoundError : If the model file does not exist.
            RuntimeError      : If the file can't be deserialised.
        """
        path = model_path or settings.CROP_MODEL_PATH

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Crop model not found at '{path}'.\n"
                "Run: python ml/generate_datasets.py && python ml/train_crop.py"
            )

        try:
            payload = joblib.load(path)
            self.pipeline      = payload["pipeline"]
            self.label_encoder = payload["label_encoder"]
            self.feature_cols  = payload["feature_cols"]
            logger.info(
                "CropPredictor loaded | path=%s | classes=%d",
                path, len(self.label_encoder.classes_),
            )
        except Exception as exc:
            logger.error("Failed to load crop model: %s", exc)
            raise RuntimeError(f"Could not load crop model: {exc}") from exc

    # ─────────────────────────────────────────────────────────────────────────
    def predict(
        self,
        N: float,
        P: float,
        K: float,
        temperature: float,
        humidity: float,
        ph: float,
        rainfall: float,
    ) -> dict[str, Any]:
        """
        Predict the recommended crop.

        Args:
            N           : Nitrogen content (mg/kg)
            P           : Phosphorus content (mg/kg)
            K           : Potassium content (mg/kg)
            temperature : Temperature in Celsius
            humidity    : Relative humidity (%)
            ph          : Soil pH (0–14)
            rainfall    : Rainfall in mm

        Returns:
            dict with keys:
                "prediction"  : str  — predicted crop name
                "confidence"  : float — max class probability (0.0–1.0)
                "all_probs"   : dict  — {crop_name: probability} for all classes
        """
        # Build feature array in the exact order the model was trained on
        features = np.array([[N, P, K, temperature, humidity, ph, rainfall]])

        # ── Predict ────────────────────────────────────────────────────────
        pred_enc = self.pipeline.predict(features)[0]
        proba    = self.pipeline.predict_proba(features)[0]

        # ── Decode label ───────────────────────────────────────────────────
        pred_label = self.label_encoder.inverse_transform([pred_enc])[0]
        confidence = float(proba.max())

        # ── All class probabilities (optional enrichment) ──────────────────
        all_probs = {
            self.label_encoder.inverse_transform([i])[0]: round(float(p), 4)
            for i, p in enumerate(proba)
        }

        logger.info(
            "Crop prediction | N=%.1f P=%.1f K=%.1f ph=%.1f → %s (conf=%.2f)",
            N, P, K, ph, pred_label, confidence,
        )

        return {
            "prediction": pred_label,
            "confidence": round(confidence, 4),
            "all_probs":  all_probs,
        }

    # ─────────────────────────────────────────────────────────────────────────
    @property
    def classes(self) -> list[str]:
        """Return sorted list of all crop classes the model can predict."""
        return sorted(self.label_encoder.classes_.tolist())
