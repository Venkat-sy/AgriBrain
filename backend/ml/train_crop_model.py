"""
backend/ml/train_crop_model.py
==============================
Multi-dataset XGBoost Crop Recommendation training pipeline.

- Dynamically ingests every CSV in  backend/ml/datasets/
- Standardises column names -> N, P, K, temperature, humidity, ph, rainfall, label
- Handles duplicates, nulls (median imputation for features)
- Trains an XGBClassifier with RandomizedSearchCV hyper-tuning
- Persists  {model, label_encoder, feature_columns}  as a single joblib bundle
  to  backend/ml/saved_models/xgboost_crop_model.joblib
"""

from __future__ import annotations

import glob
import os
import sys
import warnings
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from scipy.stats import randint, uniform
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from xgboost import XGBClassifier
import joblib

warnings.filterwarnings("ignore")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent            # backend/ml/
DATASETS_DIR = SCRIPT_DIR / "datasets"
SAVED_MODELS_DIR = SCRIPT_DIR / "saved_models"
OUTPUT_PATH = SAVED_MODELS_DIR / "xgboost_crop_model.joblib"

FEATURE_COLUMNS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_COLUMN = "label"

# Common aliases found across different CSV sources -> canonical names
COLUMN_ALIASES: Dict[str, str] = {
    # Nitrogen
    "n": "N", "nitrogen": "N", "n_ratio": "N", "nitrogen_ratio": "N",
    # Phosphorus
    "p": "P", "phosphorus": "P", "p_ratio": "P", "phosphorus_ratio": "P",
    # Potassium
    "k": "K", "potassium": "K", "k_ratio": "K", "potassium_ratio": "K",
    # Temperature
    "temperature": "temperature", "temp": "temperature", "temperature_c": "temperature",
    "avg_temp": "temperature", "avg_temperature": "temperature",
    # Humidity
    "humidity": "humidity", "humidity_percent": "humidity",
    "relative_humidity": "humidity", "avg_humidity": "humidity",
    # pH
    "ph": "ph", "ph_value": "ph", "soil_ph": "ph",
    # Rainfall
    "rainfall": "rainfall", "rainfall_mm": "rainfall",
    "annual_rainfall": "rainfall", "avg_rainfall": "rainfall",
    # Label
    "label": "label", "crop": "label", "crop_name": "label",
    "crop_type": "label", "target": "label", "class": "label",
}


def _standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to the canonical feature names."""
    rename_map: Dict[str, str] = {}
    for col in df.columns:
        key = col.strip().lower().replace(" ", "_")
        if key in COLUMN_ALIASES:
            rename_map[col] = COLUMN_ALIASES[key]
    df = df.rename(columns=rename_map)
    return df


def ingest_datasets() -> pd.DataFrame:
    """Read every CSV in the datasets/ directory, standardise, and merge."""
    csv_paths = sorted(glob.glob(str(DATASETS_DIR / "*.csv")))
    if not csv_paths:
        print("ERROR: No CSV files found in " + str(DATASETS_DIR))
        sys.exit(1)

    frames: List[pd.DataFrame] = []
    for path in csv_paths:
        print("  [+] Loading " + os.path.basename(path) + " ...", end=" ")
        df = pd.read_csv(path)
        df = _standardise_columns(df)

        # Keep only the columns we care about
        available = [c for c in FEATURE_COLUMNS + [TARGET_COLUMN] if c in df.columns]
        missing = set(FEATURE_COLUMNS + [TARGET_COLUMN]) - set(available)
        if missing:
            print("SKIPPED (missing columns: " + str(missing) + ")")
            continue

        df = df[FEATURE_COLUMNS + [TARGET_COLUMN]]
        print(str(len(df)) + " rows")
        frames.append(df)

    if not frames:
        print("ERROR: No valid datasets found after column validation.")
        sys.exit(1)

    master = pd.concat(frames, ignore_index=True)
    print("")
    print("  -> Combined raw rows: " + str(len(master)))

    # --- Drop unnamed index columns that sneak in as 'Unnamed: 0' etc. ---
    unnamed_cols = [c for c in master.columns if c.startswith("Unnamed")]
    if unnamed_cols:
        master.drop(columns=unnamed_cols, inplace=True)

    # --- Deduplicate ---
    before = len(master)
    master.drop_duplicates(inplace=True)
    dupes = before - len(master)
    if dupes:
        print("  -> Dropped " + str(dupes) + " duplicate rows")

    # --- Handle nulls ---
    # Features: median imputation
    for col in FEATURE_COLUMNS:
        n_null = master[col].isnull().sum()
        if n_null > 0:
            median_val = master[col].median()
            master[col].fillna(median_val, inplace=True)
            print("  -> Filled " + str(n_null) + " nulls in '" + col + "' with median=" + str(round(median_val, 2)))

    # Target: drop rows with no label (can't impute a class)
    label_nulls = master[TARGET_COLUMN].isnull().sum()
    if label_nulls > 0:
        master.dropna(subset=[TARGET_COLUMN], inplace=True)
        print("  -> Dropped " + str(label_nulls) + " rows with null labels")

    # Normalise label casing (e.g. 'Rice' vs 'rice')
    master[TARGET_COLUMN] = master[TARGET_COLUMN].str.strip().str.lower()

    print("  -> Final clean rows: " + str(len(master)))
    print("  -> Unique crops: " + str(master[TARGET_COLUMN].nunique()))
    return master.reset_index(drop=True)


def train(df: pd.DataFrame) -> None:
    """Train XGBClassifier with RandomizedSearchCV and persist the bundle."""

    X = df[FEATURE_COLUMNS].astype(float)
    y_raw = df[TARGET_COLUMN]

    # --- Encode labels ---
    le = LabelEncoder()
    y = le.fit_transform(y_raw)
    num_classes = len(le.classes_)
    print("")
    print("  Classes (" + str(num_classes) + "): " + str(list(le.classes_)))

    # --- Train / test split ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("  Train: " + str(len(X_train)) + "  |  Test: " + str(len(X_test)))

    # --- Compute per-class sample weights for imbalance ---
    class_counts = np.bincount(y_train)
    total = len(y_train)
    class_weights = {i: total / (num_classes * c) for i, c in enumerate(class_counts) if c > 0}
    sample_weights = np.array([class_weights[label] for label in y_train])

    # --- Base estimator ---
    base_xgb = XGBClassifier(
        objective="multi:softprob",
        num_class=num_classes,
        eval_metric="mlogloss",
        use_label_encoder=False,
        tree_method="hist",
        random_state=42,
        verbosity=0,
    )

    # --- Hyper-parameter search space ---
    param_dist = {
        "n_estimators": randint(100, 500),
        "max_depth": randint(3, 12),
        "learning_rate": uniform(0.01, 0.29),
    }

    search = RandomizedSearchCV(
        estimator=base_xgb,
        param_distributions=param_dist,
        n_iter=30,
        scoring="accuracy",
        cv=5,
        random_state=42,
        n_jobs=-1,
        verbose=0,
    )

    print("")
    print("  Running RandomizedSearchCV (30 iters x 5-fold) ...")
    search.fit(X_train, y_train, sample_weight=sample_weights)

    best = search.best_estimator_
    print("  Best params: " + str(search.best_params_))
    print("  Best CV accuracy: " + str(round(search.best_score_, 4)))

    # --- Evaluate on held-out test set ---
    y_pred = best.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print("")
    print("  TEST-SET ACCURACY: " + str(round(acc, 4)))
    print("")
    print(classification_report(
        y_test, y_pred, target_names=le.classes_, zero_division=0
    ))

    # --- Persist model bundle ---
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)
    bundle = {
        "model": best,
        "label_encoder": le,
        "feature_columns": FEATURE_COLUMNS,
        "num_classes": num_classes,
        "classes": list(le.classes_),
        "best_params": search.best_params_,
        "test_accuracy": acc,
    }
    joblib.dump(bundle, OUTPUT_PATH, compress=3)
    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print("  Model saved -> " + str(OUTPUT_PATH))
    print("  File size: " + str(round(size_kb, 1)) + " KB")


def main() -> None:
    print("=" * 60)
    print("  XGBoost Crop Recommendation -- Training Pipeline")
    print("=" * 60)

    print("")
    print("[1/2] Ingesting datasets ...")
    df = ingest_datasets()

    print("")
    print("[2/2] Training XGBClassifier ...")
    train(df)

    print("")
    print("=" * 60)
    print("  DONE: Pipeline complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
import pandas as pd
import numpy as np
import joblib
from scipy.stats import uniform, randint
from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
