"""
services/fertilizer_predictor.py
---------------------------------
Service class that loads the trained fertilizer model and exposes a
predict() method used by the FastAPI prediction router.

Unlike the crop model, the fertilizer model requires categorical inputs
(Soil Type, Crop Type) that must be encoded with the saved LabelEncoders
before passing to the pipeline.
"""

import logging
import os
from typing import Any

import numpy as np
import joblib

from backend.config import settings

# ─── Logger ──────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)


class FertilizerPredictor:
    """
    Wrapper around the trained fertilizer recommendation pipeline.

    Attributes:
        pipeline         : Trained sklearn Pipeline (StandardScaler + RFC)
        label_encoder    : LabelEncoder for target (fertilizer names)
        soil_encoder     : LabelEncoder for 'Soil Type' feature
        crop_encoder     : LabelEncoder for 'Crop Type' feature
        numeric_cols     : Ordered numeric feature names
        categorical_cols : Categorical feature names
    """

    def __init__(self, model_path: str | None = None):
        """
        Load the serialised fertilizer model from disk.

        Args:
            model_path : Path to the .pkl file.
                         Defaults to settings.FERTILIZER_MODEL_PATH.

        Raises:
            FileNotFoundError : Model file not found.
            RuntimeError      : Deserialisation failure.
        """
        path = model_path or settings.FERTILIZER_MODEL_PATH

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Fertilizer model not found at '{path}'.\n"
                "Run: python ml/generate_datasets.py && python ml/train_fertilizer.py"
            )

        try:
            payload = joblib.load(path)
            self.pipeline         = payload["pipeline"]
            self.label_encoder    = payload["label_encoder"]
            self.soil_encoder     = payload["soil_encoder"]
            self.crop_encoder     = payload["crop_encoder"]
            self.numeric_cols     = payload["numeric_cols"]
            self.categorical_cols = payload["categorical_cols"]
            logger.info(
                "FertilizerPredictor loaded | path=%s | classes=%d | soil_types=%s | crop_types=%s",
                path,
                len(self.label_encoder.classes_),
                list(self.soil_encoder.classes_),
                list(self.crop_encoder.classes_),
            )
        except Exception as exc:
            logger.error("Failed to load fertilizer model: %s", exc)
            raise RuntimeError(f"Could not load fertilizer model: {exc}") from exc

    # ─────────────────────────────────────────────────────────────────────────
    def _encode_soil_type(self, soil_type: str) -> int:
        """
        Encode a soil type string using the saved LabelEncoder.
        Falls back gracefully if unseen label is passed.
        """
        soil_type = soil_type.strip().title()
        known = self.soil_encoder.classes_

        if soil_type not in known:
            logger.warning(
                "Unknown soil_type '%s'. Known types: %s. Defaulting to '%s'.",
                soil_type, list(known), known[0],
            )
            soil_type = known[0]

        return int(self.soil_encoder.transform([soil_type])[0])

    def _encode_crop_type(self, crop_type: str) -> int:
        """
        Encode a crop type string using the saved LabelEncoder.
        Falls back gracefully if unseen label is passed.
        """
        crop_type = crop_type.strip().title()
        known = self.crop_encoder.classes_

        if crop_type not in known:
            logger.warning(
                "Unknown crop_type '%s'. Known types: %s. Defaulting to '%s'.",
                crop_type, list(known), known[0],
            )
            crop_type = known[0]

        return int(self.crop_encoder.transform([crop_type])[0])

    # ─────────────────────────────────────────────────────────────────────────
    def predict(
        self,
        temperature: float,
        humidity: float,
        moisture: float,
        soil_type: str,
        crop_type: str,
        N: float,
        P: float,
        K: float,
    ) -> dict[str, Any]:
        """
        Predict the recommended fertilizer.

        Args:
            temperature : Temperature in Celsius
            humidity    : Relative humidity (%)
            moisture    : Soil moisture (%)
            soil_type   : One of Sandy, Loamy, Black, Red, Clayey
            crop_type   : Crop being grown (e.g., Paddy, Wheat, Maize)
            N           : Nitrogen content (mg/kg)
            P           : Phosphorus content (mg/kg)
            K           : Potassium content (mg/kg)

        Returns:
            dict with keys:
                "prediction"  : str   — recommended fertilizer name
                "confidence"  : float — max class probability
                "all_probs"   : dict  — {fertilizer: probability} for all classes
        """
        # ── Encode categoricals ────────────────────────────────────────────
        soil_enc = self._encode_soil_type(soil_type)
        crop_enc = self._encode_crop_type(crop_type)

        # ── Assemble feature vector ────────────────────────────────────────
        # Order must match training: [Temperature, Humidity, Moisture,
        #                             Nitrogen, Potassium, Phosphorous,
        #                             Soil Type (enc), Crop Type (enc)]
        features = np.array([[
            temperature, humidity, moisture,
            N, K, P,          # Note: training order is N, K, P (Potassium before Phosphorous)
            soil_enc, crop_enc,
        ]])

        # ── Predict ────────────────────────────────────────────────────────
        pred_enc  = self.pipeline.predict(features)[0]
        proba     = self.pipeline.predict_proba(features)[0]
        pred_label = self.label_encoder.inverse_transform([pred_enc])[0]
        confidence = float(proba.max())

        # ── All class probabilities ────────────────────────────────────────
        all_probs = {
            self.label_encoder.inverse_transform([i])[0]: round(float(p), 4)
            for i, p in enumerate(proba)
        }

        logger.info(
            "Fertilizer prediction | soil=%s crop=%s N=%.1f → %s (conf=%.2f)",
            soil_type, crop_type, N, pred_label, confidence,
        )

        return {
            "prediction": pred_label,
            "confidence": round(confidence, 4),
            "all_probs":  all_probs,
        }

    # ─────────────────────────────────────────────────────────────────────────
    @property
    def fertilizers(self) -> list[str]:
        """Return sorted list of all fertilizer classes the model can predict."""
        return sorted(self.label_encoder.classes_.tolist())

    @property
    def soil_types(self) -> list[str]:
        """Return list of soil types known to the model."""
        return sorted(self.soil_encoder.classes_.tolist())

    @property
    def crop_types(self) -> list[str]:
        """Return list of crop types known to the model."""
        return sorted(self.crop_encoder.classes_.tolist())
