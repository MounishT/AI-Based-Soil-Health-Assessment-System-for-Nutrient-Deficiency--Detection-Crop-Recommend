"""
ml/train_crop.py
----------------
Training script for the Crop Recommendation RandomForestClassifier.

Dataset:
    data/Crop_recommendation.csv
    Columns: N, P, K, temperature, humidity, ph, rainfall, label

Output:
    models/crop_model.pkl   → serialised pipeline (scaler + classifier)

Usage:
    python ml_training/train_crop.py

The script:
    1. Loads and validates the CSV
    2. Encodes labels
    3. Scales features with StandardScaler
    4. Trains a RandomForestClassifier with cross-validation
    5. Prints classification report + feature importances
    6. Saves the model pipeline with joblib
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
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

# ─── Logger ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ─── Paths ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "Crop_recommendation.csv")
MODEL_PATH   = os.path.join(BASE_DIR, "models", "crop_model.pkl")

# ─── Feature columns expected in the CSV ─────────────────────────────────────
FEATURE_COLS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COL   = "label"


def load_and_validate(path: str) -> pd.DataFrame:
    """
    Load CSV and verify all required columns are present.

    Raises:
        FileNotFoundError  if the CSV file does not exist.
        ValueError         if required columns are missing.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Dataset not found: {path}\n"
            "Run `python ml_training/generate_datasets.py` to create sample data, "
            "or place the real CSV at the path above."
        )

    df = pd.read_csv(path)
    missing = [c for c in FEATURE_COLS + [TARGET_COL] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in dataset: {missing}")

    logger.info("Dataset loaded | rows=%d  classes=%d", len(df), df[TARGET_COL].nunique())
    return df


def train(df: pd.DataFrame):
    """
    Full training pipeline:
        1. Feature / label split
        2. Train-test split (80 / 20, stratified)
        3. Build Pipeline: StandardScaler → RandomForestClassifier
        4. 5-fold cross-validation
        5. Evaluate on held-out test set
        6. Save model + label encoder

    Args:
        df : Validated crop recommendation DataFrame.
    """
    # ── 1. Prepare features & labels ──────────────────────────────────────
    X = df[FEATURE_COLS].values
    y = df[TARGET_COL].values

    # Encode string labels → integers (stored alongside the pipeline)
    le = LabelEncoder()
    y_enc = le.fit_transform(y)
    class_names = le.classes_
    logger.info("Classes (%d): %s", len(class_names), list(class_names))

    # ── 2. Train / test split ─────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc,
        test_size=0.20,
        random_state=42,
        stratify=y_enc,
    )
    logger.info("Train size=%d  Test size=%d", len(X_train), len(X_test))

    # ── 3. Pipeline: Scaler + RandomForest ────────────────────────────────
    clf = RandomForestClassifier(
        n_estimators=200,       # number of trees
        max_depth=None,         # grow full trees
        min_samples_split=2,
        min_samples_leaf=1,
        max_features="sqrt",    # standard for classification
        random_state=42,
        n_jobs=-1,              # use all CPU cores
        class_weight="balanced",# handle class imbalance
    )

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        ("clf",    clf),
    ])

    # ── 4. Cross-validation ───────────────────────────────────────────────
    logger.info("Running 5-fold stratified cross-validation ...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="accuracy", n_jobs=-1)
    logger.info(
        "CV Accuracy: %.4f  (+/- %.4f)",
        cv_scores.mean(), cv_scores.std() * 2,
    )

    # ── 5. Final fit on full training set ─────────────────────────────────
    logger.info("Fitting final model on full training set ...")
    pipeline.fit(X_train, y_train)

    # ── 6. Evaluate on test set ───────────────────────────────────────────
    y_pred = pipeline.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    logger.info("Test Accuracy: %.4f", acc)

    print("\n" + "=" * 60)
    print("CLASSIFICATION REPORT — CROP RECOMMENDATION MODEL")
    print("=" * 60)
    print(classification_report(y_test, y_pred, target_names=class_names))

    # Feature importance (from the random forest, not the pipeline scaler)
    importances = pipeline.named_steps["clf"].feature_importances_
    feat_imp = sorted(zip(FEATURE_COLS, importances), key=lambda x: x[1], reverse=True)
    print("FEATURE IMPORTANCES:")
    for feat, imp in feat_imp:
        bar = "#" * int(imp * 50)
        print(f"  {feat:<15} {imp:.4f}  {bar}")
    print("=" * 60 + "\n")

    return pipeline, le


def save_model(pipeline: Pipeline, label_encoder: LabelEncoder, path: str) -> None:
    """
    Serialise the trained pipeline and label encoder together as a dict.

    Saved object structure:
        {
            "pipeline":      <sklearn.pipeline.Pipeline>,
            "label_encoder": <sklearn.preprocessing.LabelEncoder>,
            "feature_cols":  ["N", "P", "K", ...],
        }
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "pipeline":      pipeline,
        "label_encoder": label_encoder,
        "feature_cols":  FEATURE_COLS,
    }
    joblib.dump(payload, path, compress=3)
    size_kb = os.path.getsize(path) / 1024
    logger.info("Model saved → %s  (%.1f KB)", path, size_kb)


def verify_model(path: str) -> None:
    """Quick sanity-check: load the saved model and run one prediction."""
    payload   = joblib.load(path)
    pipeline  = payload["pipeline"]
    le        = payload["label_encoder"]
    # Sample input: Rice-like conditions
    sample = np.array([[90, 42, 43, 25.0, 80.0, 6.5, 202.0]])
    pred_enc  = pipeline.predict(sample)[0]
    pred_prob = pipeline.predict_proba(sample).max()
    pred_label = le.inverse_transform([pred_enc])[0]
    logger.info(
        "Sanity check — Input: N=90 P=42 K=43 temp=25 hum=80 ph=6.5 rain=202 → Predicted: %s  (conf=%.2f)",
        pred_label, pred_prob,
    )


# ─── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("=== Crop Recommendation Model Training ===")

    # 1. Load
    df = load_and_validate(DATASET_PATH)

    # 2. Train
    pipeline, le = train(df)

    # 3. Save
    save_model(pipeline, le, MODEL_PATH)

    # 4. Verify
    verify_model(MODEL_PATH)

    logger.info("Done. Model ready at: %s", MODEL_PATH)
