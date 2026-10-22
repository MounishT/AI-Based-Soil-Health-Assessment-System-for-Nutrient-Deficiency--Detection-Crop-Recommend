"""
ml/train_fertilizer.py
----------------------
Training script for the Fertilizer Recommendation RandomForestClassifier.

Dataset:
    data/fertilizer_recommendation.csv
    Columns: Temperature, Humidity, Moisture, Soil Type, Crop Type,
             Nitrogen, Potassium, Phosphorous, Fertilizer Name

Output:
    models/fertilizer_model.pkl  → serialised pipeline + encoders

Usage:
    python ml_training/train_fertilizer.py

The script:
    1. Loads and validates the CSV
    2. Label-encodes categorical columns (Soil Type, Crop Type)
    3. Scales numeric features with StandardScaler
    4. Trains a RandomForestClassifier with cross-validation
    5. Prints classification report + feature importances
    6. Saves the full pipeline + all encoders with joblib
"""

import os
import sys
import logging

import numpy as np
import pandas as pd
import joblib

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report, accuracy_score

# ─── Logger ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "fertilizer_recommendation.csv")
MODEL_PATH   = os.path.join(BASE_DIR, "models", "fertilizer_model.pkl")

# ─── Column definitions ───────────────────────────────────────────────────────
NUMERIC_COLS      = ["Temperature", "Humidity", "Moisture", "Nitrogen", "Potassium", "Phosphorous"]
CATEGORICAL_COLS  = ["Soil Type", "Crop Type"]
TARGET_COL        = "Fertilizer Name"

# Final feature order fed into the model (numeric first, then encoded categoricals)
FEATURE_ORDER = NUMERIC_COLS + CATEGORICAL_COLS   # for documentation only


def load_and_validate(path: str) -> pd.DataFrame:
    """
    Load CSV and verify all required columns are present.

    Raises:
        FileNotFoundError if the CSV does not exist.
        ValueError        if required columns are missing.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Run `python ml_training/generate_datasets.py` to create sample data, "
            "or place the real CSV at the path above."
        )

    df = pd.read_csv(path)

    # Rename columns from the new real dataset to match our API schema
    rename_map = {
        'Soil_Type': 'Soil Type',
        'Soil_Moisture': 'Moisture',
        'Nitrogen_Level': 'Nitrogen',
        'Phosphorus_Level': 'Phosphorous',
        'Potassium_Level': 'Potassium',
        'Crop_Type': 'Crop Type',
        'Recommended_Fertilizer': 'Fertilizer Name'
    }
    df = df.rename(columns=rename_map)

    required = NUMERIC_COLS + CATEGORICAL_COLS + [TARGET_COL]
    missing  = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    logger.info("Dataset loaded | rows=%d  fertilizer classes=%d", len(df), df[TARGET_COL].nunique())
    return df


def encode_features(df: pd.DataFrame):
    """
    Encode categorical columns and build a feature matrix.

    Returns:
        X              : np.ndarray of shape (n_samples, n_features)
        y_enc          : np.ndarray of integer-encoded target labels
        label_encoder  : fitted LabelEncoder for the target
        soil_encoder   : fitted LabelEncoder for Soil Type
        crop_encoder   : fitted LabelEncoder for Crop Type
    """
    # ── Encode target ──────────────────────────────────────────────────────
    le_target = LabelEncoder()
    y_enc = le_target.fit_transform(df[TARGET_COL].values)

    # ── Encode categorical features ────────────────────────────────────────
    le_soil = LabelEncoder()
    le_crop = LabelEncoder()

    soil_enc = le_soil.fit_transform(df["Soil Type"].values)
    crop_enc = le_crop.fit_transform(df["Crop Type"].values)

    # ── Assemble feature matrix ────────────────────────────────────────────
    X_numeric = df[NUMERIC_COLS].values.astype(float)
    X = np.column_stack([X_numeric, soil_enc, crop_enc])

    logger.info(
        "Feature matrix shape: %s  |  Target classes (%d): %s",
        X.shape, len(le_target.classes_), list(le_target.classes_),
    )
    return X, y_enc, le_target, le_soil, le_crop


def train(X: np.ndarray, y_enc: np.ndarray, class_names: list):
    """
    Build and train a Pipeline: StandardScaler → RandomForestClassifier.

    Returns:
        Fitted pipeline.
    """
    # ── Train / test split ────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc,
        test_size=0.20,
        random_state=42,
        stratify=y_enc,
    )
    logger.info("Train size=%d  Test size=%d", len(X_train), len(X_test))

    # ── Pipeline ──────────────────────────────────────────────────────────
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="sqrt",
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    clf),
    ])

    # ── Cross-validation ──────────────────────────────────────────────────
    logger.info("Running 5-fold stratified cross-validation ...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1)
    logger.info(
        "CV Accuracy: %.4f  (+/- %.4f)",
        cv_scores.mean(), cv_scores.std() * 2,
    )

    # ── Final fit ─────────────────────────────────────────────────────────
    logger.info("Fitting final model on full training set ...")
    pipeline.fit(X_train, y_train)

    # ── Test evaluation ───────────────────────────────────────────────────
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info("Test Accuracy: %.4f", acc)

    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT — FERTILIZER RECOMMENDATION MODEL")
    print("=" * 60)
    print(classification_report(y_test, y_pred, target_names=class_names))

    # ── Feature importance ────────────────────────────────────────────────
    feature_names = NUMERIC_COLS + ["Soil Type (enc)", "Crop Type (enc)"]
    importances   = pipeline.named_steps["clf"].feature_importances_
    feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
    print("FEATURE IMPORTANCES:")
    for feat, imp in feat_imp:
        bar = "#" * int(imp * 50)
        print(f"  {feat:<20} {imp:.4f}  {bar}")
    print("=" * 60 + "\n")

    return pipeline


def save_model(
    pipeline,
    le_target: LabelEncoder,
    le_soil: LabelEncoder,
    le_crop: LabelEncoder,
    path: str,
) -> None:
    """
    Serialise the pipeline and all encoders together.

    Saved object structure:
        {
            "pipeline":        <Pipeline>,
            "label_encoder":   <LabelEncoder for target>,
            "soil_encoder":    <LabelEncoder for Soil Type>,
            "crop_encoder":    <LabelEncoder for Crop Type>,
            "numeric_cols":    [...],
            "categorical_cols": [...],
        }
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "pipeline":         pipeline,
        "label_encoder":    le_target,
        "soil_encoder":     le_soil,
        "crop_encoder":     le_crop,
        "numeric_cols":     NUMERIC_COLS,
        "categorical_cols": CATEGORICAL_COLS,
    }
    joblib.dump(payload, path, compress=3)
    size_kb = os.path.getsize(path) / 1024
    logger.info("Model saved → %s  (%.1f KB)", path, size_kb)


def verify_model(path: str) -> None:
    """Sanity-check: load saved model and run a test prediction."""
    payload  = joblib.load(path)
    pipeline = payload["pipeline"]
    le       = payload["label_encoder"]
    le_soil  = payload["soil_encoder"]
    le_crop  = payload["crop_encoder"]

    # Sample: Clay soil, Rice crop, low N
    soil_enc = le_soil.transform(["Clayey"])[0]
    crop_enc = le_crop.transform(["Paddy"])[0]
    sample = np.array([[26.0, 52.0, 38.0, 37.0, 0.0, 0.0, soil_enc, crop_enc]])

    pred_enc   = pipeline.predict(sample)[0]
    pred_prob  = pipeline.predict_proba(sample).max()
    pred_label = le.inverse_transform([pred_enc])[0]
    logger.info(
        "Sanity check — Clay/Rice/N=37 → Predicted: %s  (conf=%.2f)",
        pred_label, pred_prob,
    )


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("=== Fertilizer Recommendation Model Training ===")

    # 1. Load
    df = load_and_validate(DATASET_PATH)

    # 2. Encode
    X, y_enc, le_target, le_soil, le_crop = encode_features(df)
    class_names = list(le_target.classes_)

    # 3. Train
    pipeline = train(X, y_enc, class_names)

    # 4. Save
    save_model(pipeline, le_target, le_soil, le_crop, MODEL_PATH)

    # 5. Verify
    verify_model(MODEL_PATH)

    logger.info("Done. Model ready at: %s", MODEL_PATH)
