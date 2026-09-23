"""
Stage 4: Core Machine Learning Development
===========================================
AI-Driven Nutrient Recommendation System

Trains Random Forest and XGBoost models for:
  1. Crop Recommendation (classification, 22 classes)
  2. Fertilizer Recommendation (classification, 14 classes)
  3. Yield Prediction (regression)
  4. Advanced Yield — multi-output (Yield regression, Irrigation regression, Risk classification)

For each task, both models are saved and the best is selected based on validation performance.
Final metrics are reported on the held-out test set.
All results are saved to models/model_evaluation_results.json.
"""

import os
import json
import time
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (
    accuracy_score, f1_score, classification_report,
    mean_squared_error, r2_score, mean_absolute_error,
    confusion_matrix
)
import warnings
warnings.filterwarnings('ignore')

# Try importing xgboost
try:
    from xgboost import XGBClassifier, XGBRegressor
    HAS_XGB = True
except ImportError:
    print("WARNING: xgboost not installed. Only Random Forest models will be trained.")
    HAS_XGB = False

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = r"c:\Users\USER\Downloads\FinalYearProject"
TRAIN_DIR = os.path.join(BASE_DIR, "training_data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODELS_DIR, exist_ok=True)

with open(os.path.join(TRAIN_DIR, "feature_config.json"), "r") as f:
    config = json.load(f)

# Store all evaluation results
all_results = {}

# ─── Hyperparameter Grids ───────────────────────────────────────────────────

RF_CLF_PARAMS = {
    "n_estimators": [100, 200],
    "max_depth": [None, 20, 30],
    "min_samples_split": [2, 5],
}

XGB_CLF_PARAMS = {
    "n_estimators": [100, 200],
    "max_depth": [6, 10],
    "learning_rate": [0.1, 0.05],
}

RF_REG_PARAMS = {
    "n_estimators": [100, 200],
    "max_depth": [None, 20],
    "min_samples_split": [2, 5],
}

XGB_REG_PARAMS = {
    "n_estimators": [100, 200],
    "max_depth": [6, 10],
    "learning_rate": [0.1, 0.05],
}


# ─── Evaluation Helpers ─────────────────────────────────────────────────────

def evaluate_classification(model, X, y, label=""):
    """Evaluate a classification model and return a metrics dict."""
    preds = model.predict(X)
    acc = accuracy_score(y, preds)
    f1_macro = f1_score(y, preds, average='macro')
    f1_weighted = f1_score(y, preds, average='weighted')
    cm = confusion_matrix(y, preds).tolist()
    report = classification_report(y, preds, output_dict=True, zero_division=0)
    metrics = {
        "accuracy": round(acc, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "confusion_matrix": cm,
        "classification_report": report,
    }
    if label:
        print(f"    {label}: Acc={acc:.4f}, F1(macro)={f1_macro:.4f}, F1(weighted)={f1_weighted:.4f}")
    return metrics


def evaluate_regression(model, X, y, label=""):
    """Evaluate a regression model and return a metrics dict."""
    preds = model.predict(X)
    rmse = np.sqrt(mean_squared_error(y, preds))
    mae = mean_absolute_error(y, preds)
    r2 = r2_score(y, preds)
    metrics = {
        "rmse": round(rmse, 4),
        "mae": round(mae, 4),
        "r2": round(r2, 4),
    }
    if label:
        print(f"    {label}: RMSE={rmse:.4f}, MAE={mae:.4f}, R²={r2:.4f}")
    return metrics

# ---------------------------------------------------------------------------
# Updated training utilities – modernized implementations
# ---------------------------------------------------------------------------
from sklearn.model_selection import train_test_split, StratifiedKFold
from datetime import datetime

def _load_data(task_name: str):
    """Load the appropriate CSV for a given task.

    Returns
    -------
    X : pandas.DataFrame
        Feature matrix.
    y : pandas.Series
        Target vector.
    """
    mapping = {
        "crop_recommendation": "crop_recommendation_train.csv",
        "fertilizer_recommendation": "fertilizer_recommendation_train.csv",
        "yield_prediction": "yield_prediction_train.csv",
        "advanced_yield": "advanced_yield_train.csv",
    }
    file_name = mapping.get(task_name)
    if not file_name:
        raise ValueError(f"Unsupported task {task_name}")
    df = pd.read_csv(os.path.join(TRAIN_DIR, file_name))
    # Determine target column based on task
    if task_name == "crop_recommendation":
        target_col = "label_encoded"
    elif task_name == "fertilizer_recommendation":
        target_col = "Fertilizer_Encoded"
    elif task_name == "yield_prediction":
        target_col = "Yield_per_Area"
    else:  # advanced_yield – caller will slice columns
        target_col = None
    if target_col:
        X = df.drop(columns=[target_col])
        y = df[target_col]
        return X, y
    return df, None

def _fit_model(model, X_train, y_train, X_val, y_val, is_classifier: bool):
    """Fit a model with optional early stopping for XGBoost.

    Parameters
    ----------
    model : estimator
        sklearn or xgboost estimator instance.
    X_train, y_train, X_val, y_val : arrays
        Training and validation splits.
    is_classifier : bool
        Determines early‑stopping handling.
    """
    if isinstance(model, (XGBClassifier, XGBRegressor)) and HAS_XGB:
        # XGBoost supports early stopping via eval_set
        eval_metric = "logloss" if is_classifier else "rmse"
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            eval_metric=eval_metric,
            early_stopping_rounds=10,
            verbose=False,
        )
    else:
        model.fit(X_train, y_train)
    return model

def train_classification_task(task_name: str):
    """Train classification models for the specified task.

    The function loads data, performs a stratified split, runs a grid search
    for RandomForest and (optionally) XGBoost, evaluates on a held‑out test set
    and saves the best model.
    """
    print(f"\n--- Training classification task: {task_name} ---")
    X, y = _load_data(task_name)
    # Stratified split to preserve class distribution
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    # Further split training set for validation during hyper‑parameter search
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42, stratify=y_train
    )

    # --- Random Forest ---
    rf = RandomForestClassifier(random_state=42)
    rf_grid = GridSearchCV(rf, RF_CLF_PARAMS, cv=3, n_jobs=-1, scoring="accuracy")
    rf_grid.fit(X_train, y_train)
    best_rf = rf_grid.best_estimator_
    best_rf = _fit_model(best_rf, X_train, y_train, X_val, y_val, is_classifier=True)
    rf_metrics = evaluate_classification(best_rf, X_test, y_test, label="RF")

    # --- XGBoost (optional) ---
    if HAS_XGB:
        xgb = XGBClassifier(
            use_label_encoder=False,
            eval_metric="logloss",
            random_state=42,
        )
        xgb_grid = GridSearchCV(xgb, XGB_CLF_PARAMS, cv=3, n_jobs=-1, scoring="accuracy")
        xgb_grid.fit(X_train, y_train)
        best_xgb = xgb_grid.best_estimator_
        best_xgb = _fit_model(best_xgb, X_train, y_train, X_val, y_val, is_classifier=True)
        xgb_metrics = evaluate_classification(best_xgb, X_test, y_test, label="XGB")
    else:
        best_xgb = None
        xgb_metrics = {}

    # Choose best model based on validation accuracy (using stored cv results)
    rf_val_score = rf_grid.best_score_
    xgb_val_score = xgb_grid.best_score_ if HAS_XGB else -1
    if xgb_val_score > rf_val_score:
        best_model = best_xgb
        best_name = "xgboost"
        best_metrics = xgb_metrics
    else:
        best_model = best_rf
        best_name = "rf"
        best_metrics = rf_metrics

    # Save models with timestamp versioning
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    model_path = os.path.join(MODELS_DIR, f"{best_name}_{task_name}_model_{timestamp}.pkl")
    joblib.dump(best_model, model_path)
    print(f"    ✅ Saved best {best_name} model for {task_name} to {model_path}")

    # Record results
    task_results = {
        "problem_type": "classification",
        "models": {
            "rf": {"model_path": model_path if best_name == "rf" else None, "test_metrics": rf_metrics},
            "xgboost": {"model_path": model_path if best_name == "xgboost" else None, "test_metrics": xgb_metrics},
        },
        "selected_best": best_name,
    }
    all_results[task_name] = task_results

def train_regression_task(task_name: str):
    """Train regression models for the specified task.

    Supports RandomForestRegressor and optional XGBoostRegressor.
    """
    print(f"\n--- Training regression task: {task_name} ---")
    X, y = _load_data(task_name)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )

    # Random Forest
    rf = RandomForestRegressor(random_state=42)
    rf_grid = GridSearchCV(rf, RF_REG_PARAMS, cv=3, n_jobs=-1, scoring="neg_mean_squared_error")
    rf_grid.fit(X_train, y_train)
    best_rf = rf_grid.best_estimator_
    best_rf = _fit_model(best_rf, X_train, y_train, X_val, y_val, is_classifier=False)
    rf_metrics = evaluate_regression(best_rf, X_test, y_test, label="RF")

    # XGBoost (optional)
    if HAS_XGB:
        xgb = XGBRegressor(random_state=42)
        xgb_grid = GridSearchCV(xgb, XGB_REG_PARAMS, cv=3, n_jobs=-1, scoring="neg_mean_squared_error")
        xgb_grid.fit(X_train, y_train)
        best_xgb = xgb_grid.best_estimator_
        best_xgb = _fit_model(best_xgb, X_train, y_train, X_val, y_val, is_classifier=False)
        xgb_metrics = evaluate_regression(best_xgb, X_test, y_test, label="XGB")
    else:
        best_xgb = None
        xgb_metrics = {}

    rf_val = rf_grid.best_score_
    xgb_val = xgb_grid.best_score_ if HAS_XGB else -np.inf
    if xgb_val > rf_val:
        best_model = best_xgb
        best_name = "xgboost"
        best_metrics = xgb_metrics
    else:
        best_model = best_rf
        best_name = "rf"
        best_metrics = rf_metrics

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    model_path = os.path.join(MODELS_DIR, f"{best_name}_{task_name}_model_{timestamp}.pkl")
    joblib.dump(best_model, model_path)
    print(f"    ✅ Saved best {best_name} regression model for {task_name} to {model_path}")

    task_results = {
        "problem_type": "regression",
        "models": {
            "rf": {"model_path": model_path if best_name == "rf" else None, "test_metrics": rf_metrics},
            "xgboost": {"model_path": model_path if best_name == "xgboost" else None, "test_metrics": xgb_metrics},
        },
        "selected_best": best_name,
    }
    all_results[task_name] = task_results

def train_advanced_yield():
    """Train models for the advanced yield multi‑output task.

    This function loads the advanced yield dataset and trains three separate
    models: regression for ``Yield_tons_per_ha`` and ``Irrigation_Demand_mm``,
    and classification for ``Crop_Failure_Risk``.
    """
    print("\n--- Training advanced yield multi‑output task ---")
    df = pd.read_csv(os.path.join(TRAIN_DIR, "advanced_yield_train.csv"))
    # Features are all columns except the three targets and the encoded crop type
    target_cols = {
        "yield": "Yield_tons_per_ha",
        "irrigation": "Irrigation_Demand_mm",
        "risk": "Crop_Failure_Risk",
    }
    feature_cols = [c for c in df.columns if c not in list(target_cols.values()) + ["Crop_Type_Encoded"]]
    X = df[feature_cols]

    sub_results = {}
    for sub_name, target in target_cols.items():
        y = df[target]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y if sub_name == "risk" else None
        )
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=0.2, random_state=42, stratify=y_train if sub_name == "risk" else None
        )
        if sub_name == "risk":
            # Classification
            model = RandomForestClassifier(random_state=42)
            grid = GridSearchCV(model, RF_CLF_PARAMS, cv=3, n_jobs=-1, scoring="accuracy")
            grid.fit(X_train, y_train)
            best = grid.best_estimator_
            best = _fit_model(best, X_train, y_train, X_val, y_val, is_classifier=True)
            metrics = evaluate_classification(best, X_test, y_test, label=sub_name)
            problem = "classification"
        else:
            # Regression
            model = RandomForestRegressor(random_state=42)
            grid = GridSearchCV(model, RF_REG_PARAMS, cv=3, n_jobs=-1, scoring="neg_mean_squared_error")
            grid.fit(X_train, y_train)
            best = grid.best_estimator_
            best = _fit_model(best, X_train, y_train, X_val, y_val, is_classifier=False)
            metrics = evaluate_regression(best, X_test, y_test, label=sub_name)
            problem = "regression"
        # Save model
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        model_path = os.path.join(MODELS_DIR, f"best_adv_{sub_name}_{timestamp}.pkl")
        joblib.dump(best, model_path)
        sub_results[sub_name] = {
            "problem_type": problem,
            "models": {
                "rf": {"model_path": model_path, "test_metrics": metrics}
            },
            "selected_best": "rf",
        }
        print(f"    ✅ Trained {problem} model for {sub_name} – saved to {model_path}")

    all_results["advanced_yield"] = {"sub_tasks": sub_results}


# ─── Training Functions ─────────────────────────────────────────────────────

def train_classification_task(task_name):
    """Train RF + XGB classifiers with hyperparameter tuning, select best on validation,
    evaluate on test, and save all models."""
    print(f"\n{'='*60}")
    print(f"  TASK: {task_name} (Classification)")
    print(f"{'='*60}")
    
    cfg = config[task_name]
    target_col = cfg["target_column"]
    features = cfg["input_features"]

    # Load data
    try:
        train_df = pd.read_csv(os.path.join(TRAIN_DIR, f"{task_name}_train.csv"))
        val_df = pd.read_csv(os.path.join(TRAIN_DIR, f"{task_name}_val.csv"))
        test_df = pd.read_csv(os.path.join(TRAIN_DIR, f"{task_name}_test.csv"))
    except FileNotFoundError as e:
        print(f"  ❌ Skipping {task_name}, files not found: {e}")
        return

    X_train, y_train = train_df[features], train_df[target_col]
    X_val, y_val = val_df[features], val_df[target_col]
    X_test, y_test = test_df[features], test_df[target_col]

    print(f"  Data: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")
    print(f"  Features: {len(features)}, Classes: {len(y_train.unique())}")

    task_results = {"problem_type": "classification", "models": {}}

    # ── Random Forest with GridSearchCV ──
    print("\n  [1/2] Random Forest — GridSearchCV...")
    t0 = time.time()
    rf_grid = GridSearchCV(
        RandomForestClassifier(random_state=42, n_jobs=-1),
        RF_CLF_PARAMS, cv=3, scoring='f1_macro', n_jobs=-1, refit=True
    )
    rf_grid.fit(X_train, y_train)
    rf_best = rf_grid.best_estimator_
    rf_time = time.time() - t0
    print(f"    Best params: {rf_grid.best_params_} (took {rf_time:.1f}s)")

    rf_val_metrics = evaluate_classification(rf_best, X_val, y_val, "RF Validation")
    rf_test_metrics = evaluate_classification(rf_best, X_test, y_test, "RF Test")

    task_results["models"]["random_forest"] = {
        "best_params": rf_grid.best_params_,
        "train_time_seconds": round(rf_time, 2),
        "validation_metrics": rf_val_metrics,
        "test_metrics": rf_test_metrics,
    }

    # Save RF model
    rf_path = os.path.join(MODELS_DIR, f"rf_{task_name}_model.pkl")
    joblib.dump(rf_best, rf_path)
    print(f"    Saved: {rf_path}")

    # ── XGBoost with GridSearchCV ──
    if HAS_XGB:
        print("\n  [2/2] XGBoost — GridSearchCV...")
        t0 = time.time()
        xgb_grid = GridSearchCV(
            XGBClassifier(random_state=42, n_jobs=-1, eval_metric='mlogloss',
                          use_label_encoder=False),
            XGB_CLF_PARAMS, cv=3, scoring='f1_macro', n_jobs=-1, refit=True
        )
        xgb_grid.fit(X_train, y_train)
        xgb_best = xgb_grid.best_estimator_
        xgb_time = time.time() - t0
        print(f"    Best params: {xgb_grid.best_params_} (took {xgb_time:.1f}s)")

        xgb_val_metrics = evaluate_classification(xgb_best, X_val, y_val, "XGB Validation")
        xgb_test_metrics = evaluate_classification(xgb_best, X_test, y_test, "XGB Test")

        task_results["models"]["xgboost"] = {
            "best_params": xgb_grid.best_params_,
            "train_time_seconds": round(xgb_time, 2),
            "validation_metrics": xgb_val_metrics,
            "test_metrics": xgb_test_metrics,
        }

        xgb_path = os.path.join(MODELS_DIR, f"xgb_{task_name}_model.pkl")
        joblib.dump(xgb_best, xgb_path)
        print(f"    Saved: {xgb_path}")

        # Select best on validation F1
        if xgb_val_metrics["f1_macro"] >= rf_val_metrics["f1_macro"]:
            best_name = "xgboost"
        else:
            best_name = "random_forest"
    else:
        best_name = "random_forest"

    task_results["selected_best"] = best_name
    print(f"\n  ✅ Best model for {task_name}: {best_name}")

    # Also save as 'best_<task>_model.pkl' for downstream compatibility
    best_src = os.path.join(MODELS_DIR, f"{'xgb' if best_name == 'xgboost' else 'rf'}_{task_name}_model.pkl")
    best_dst = os.path.join(MODELS_DIR, f"best_{task_name}_model.pkl")
    joblib.dump(joblib.load(best_src), best_dst)

    all_results[task_name] = task_results


def train_regression_task(task_name):
    """Train RF + XGB regressors with hyperparameter tuning, select best on validation,
    evaluate on test, and save all models."""
    print(f"\n{'='*60}")
    print(f"  TASK: {task_name} (Regression)")
    print(f"{'='*60}")

    cfg = config[task_name]
    target_col = cfg["target_column"]
    features = cfg["input_features"]

    try:
        train_df = pd.read_csv(os.path.join(TRAIN_DIR, f"{task_name}_train.csv"))
        val_df = pd.read_csv(os.path.join(TRAIN_DIR, f"{task_name}_val.csv"))
        test_df = pd.read_csv(os.path.join(TRAIN_DIR, f"{task_name}_test.csv"))
    except FileNotFoundError as e:
        print(f"  ❌ Skipping {task_name}, files not found: {e}")
        return

    X_train, y_train = train_df[features], train_df[target_col]
    X_val, y_val = val_df[features], val_df[target_col]
    X_test, y_test = test_df[features], test_df[target_col]

    print(f"  Data: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")

    task_results = {"problem_type": "regression", "models": {}}

    # ── Random Forest ──
    print("\n  [1/2] Random Forest — GridSearchCV...")
    t0 = time.time()
    rf_grid = GridSearchCV(
        RandomForestRegressor(random_state=42, n_jobs=-1),
        RF_REG_PARAMS, cv=3, scoring='r2', n_jobs=-1, refit=True
    )
    rf_grid.fit(X_train, y_train)
    rf_best = rf_grid.best_estimator_
    rf_time = time.time() - t0
    print(f"    Best params: {rf_grid.best_params_} (took {rf_time:.1f}s)")

    rf_val_metrics = evaluate_regression(rf_best, X_val, y_val, "RF Validation")
    rf_test_metrics = evaluate_regression(rf_best, X_test, y_test, "RF Test")

    task_results["models"]["random_forest"] = {
        "best_params": rf_grid.best_params_,
        "train_time_seconds": round(rf_time, 2),
        "validation_metrics": rf_val_metrics,
        "test_metrics": rf_test_metrics,
    }

    rf_path = os.path.join(MODELS_DIR, f"rf_{task_name}_model.pkl")
    joblib.dump(rf_best, rf_path)
    print(f"    Saved: {rf_path}")

    # ── XGBoost ──
    if HAS_XGB:
        print("\n  [2/2] XGBoost — GridSearchCV...")
        t0 = time.time()
        xgb_grid = GridSearchCV(
            XGBRegressor(random_state=42, n_jobs=-1),
            XGB_REG_PARAMS, cv=3, scoring='r2', n_jobs=-1, refit=True
        )
        xgb_grid.fit(X_train, y_train)
        xgb_best = xgb_grid.best_estimator_
        xgb_time = time.time() - t0
        print(f"    Best params: {xgb_grid.best_params_} (took {xgb_time:.1f}s)")

        xgb_val_metrics = evaluate_regression(xgb_best, X_val, y_val, "XGB Validation")
        xgb_test_metrics = evaluate_regression(xgb_best, X_test, y_test, "XGB Test")

        task_results["models"]["xgboost"] = {
            "best_params": xgb_grid.best_params_,
            "train_time_seconds": round(xgb_time, 2),
            "validation_metrics": xgb_val_metrics,
            "test_metrics": xgb_test_metrics,
        }

        xgb_path = os.path.join(MODELS_DIR, f"xgb_{task_name}_model.pkl")
        joblib.dump(xgb_best, xgb_path)
        print(f"    Saved: {xgb_path}")

        # Select best on validation R²
        if xgb_val_metrics["r2"] >= rf_val_metrics["r2"]:
            best_name = "xgboost"
        else:
            best_name = "random_forest"
    else:
        best_name = "random_forest"

    task_results["selected_best"] = best_name
    print(f"\n  ✅ Best model for {task_name}: {best_name}")

    best_src = os.path.join(MODELS_DIR, f"{'xgb' if best_name == 'xgboost' else 'rf'}_{task_name}_model.pkl")
    best_dst = os.path.join(MODELS_DIR, f"best_{task_name}_model.pkl")
    joblib.dump(joblib.load(best_src), best_dst)

    all_results[task_name] = task_results


def train_advanced_yield():
    """Train models for the advanced yield multi-output task.
    
    Three separate sub-models:
      - Yield (tons/ha) → Regression
      - Irrigation Demand (mm) → Regression
      - Crop Failure Risk (0/1/2) → Classification
    """
    print(f"\n{'='*60}")
    print(f"  TASK: advanced_yield (Multi-Output)")
    print(f"{'='*60}")

    cfg = config["advanced_yield"]
    features = cfg["input_features"]
    target_cols = cfg["target_columns"]  # ['Yield_tons_per_ha', 'Irrigation_Demand_mm', 'Crop_Failure_Risk']

    try:
        train_df = pd.read_csv(os.path.join(TRAIN_DIR, "advanced_yield_train.csv"))
        val_df = pd.read_csv(os.path.join(TRAIN_DIR, "advanced_yield_val.csv"))
        test_df = pd.read_csv(os.path.join(TRAIN_DIR, "advanced_yield_test.csv"))
    except FileNotFoundError as e:
        print(f"  ❌ Skipping advanced_yield, files not found: {e}")
        return

    X_train = train_df[features]
    X_val = val_df[features]
    X_test = test_df[features]

    print(f"  Data: Train={X_train.shape}, Val={X_val.shape}, Test={X_test.shape}")
    print(f"  Targets: {target_cols}")

    task_results = {"problem_type": "multi_output", "sub_tasks": {}}

    # Define which targets are regression vs classification
    sub_tasks = [
        ("Yield_tons_per_ha", "regression"),
        ("Irrigation_Demand_mm", "regression"),
        ("Crop_Failure_Risk", "classification"),
    ]

    for target, ptype in sub_tasks:
        print(f"\n  --- Sub-task: {target} ({ptype}) ---")
        y_train = train_df[target]
        y_val = val_df[target]
        y_test = test_df[target]

        sub_result = {"problem_type": ptype, "models": {}}

        if ptype == "regression":
            # RF Regressor
            rf = RandomForestRegressor(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
            rf.fit(X_train, y_train)
            rf_val = evaluate_regression(rf, X_val, y_val, "RF Val")
            rf_test = evaluate_regression(rf, X_test, y_test, "RF Test")
            sub_result["models"]["random_forest"] = {
                "validation_metrics": rf_val, "test_metrics": rf_test
            }
            joblib.dump(rf, os.path.join(MODELS_DIR, f"rf_adv_{target}_model.pkl"))

            if HAS_XGB:
                xgb = XGBRegressor(n_estimators=200, max_depth=10, learning_rate=0.1,
                                   random_state=42, n_jobs=-1)
                xgb.fit(X_train, y_train)
                xgb_val = evaluate_regression(xgb, X_val, y_val, "XGB Val")
                xgb_test = evaluate_regression(xgb, X_test, y_test, "XGB Test")
                sub_result["models"]["xgboost"] = {
                    "validation_metrics": xgb_val, "test_metrics": xgb_test
                }
                joblib.dump(xgb, os.path.join(MODELS_DIR, f"xgb_adv_{target}_model.pkl"))

                best = "xgboost" if xgb_val["r2"] >= rf_val["r2"] else "random_forest"
            else:
                best = "random_forest"

        else:  # classification
            rf = RandomForestClassifier(n_estimators=200, max_depth=20, random_state=42, n_jobs=-1)
            rf.fit(X_train, y_train)
            rf_val = evaluate_classification(rf, X_val, y_val, "RF Val")
            rf_test = evaluate_classification(rf, X_test, y_test, "RF Test")
            # Remove large nested dicts for cleaner JSON
            rf_val_clean = {k: v for k, v in rf_val.items() if k not in ("confusion_matrix", "classification_report")}
            rf_test_clean = {k: v for k, v in rf_test.items() if k not in ("confusion_matrix", "classification_report")}
            sub_result["models"]["random_forest"] = {
                "validation_metrics": rf_val_clean, "test_metrics": rf_test_clean
            }
            joblib.dump(rf, os.path.join(MODELS_DIR, f"rf_adv_{target}_model.pkl"))

            if HAS_XGB:
                xgb = XGBClassifier(n_estimators=200, max_depth=10, learning_rate=0.1,
                                    random_state=42, n_jobs=-1, eval_metric='mlogloss',
                                    use_label_encoder=False)
                xgb.fit(X_train, y_train)
                xgb_val = evaluate_classification(xgb, X_val, y_val, "XGB Val")
                xgb_test = evaluate_classification(xgb, X_test, y_test, "XGB Test")
                xgb_val_clean = {k: v for k, v in xgb_val.items() if k not in ("confusion_matrix", "classification_report")}
                xgb_test_clean = {k: v for k, v in xgb_test.items() if k not in ("confusion_matrix", "classification_report")}
                sub_result["models"]["xgboost"] = {
                    "validation_metrics": xgb_val_clean, "test_metrics": xgb_test_clean
                }
                joblib.dump(xgb, os.path.join(MODELS_DIR, f"xgb_adv_{target}_model.pkl"))

                best = "xgboost" if xgb_val.get("f1_macro", 0) >= rf_val.get("f1_macro", 0) else "random_forest"
            else:
                best = "random_forest"

        sub_result["selected_best"] = best
        task_results["sub_tasks"][target] = sub_result
        print(f"    ✅ Best for {target}: {best}")

        # Save best model alias
        prefix = "xgb" if best == "xgboost" else "rf"
        best_src = os.path.join(MODELS_DIR, f"{prefix}_adv_{target}_model.pkl")
        best_dst = os.path.join(MODELS_DIR, f"best_adv_{target}_model.pkl")
        joblib.dump(joblib.load(best_src), best_dst)

    all_results["advanced_yield"] = task_results


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  STAGE 4: CORE ML DEVELOPMENT")
    print("  AI-Driven Nutrient Recommendation System")
    print("=" * 60)
    start = time.time()

    # 1. Classification tasks
    train_classification_task("crop_recommendation")
    train_classification_task("fertilizer_recommendation")

    # 2. Regression task
    train_regression_task("yield_prediction")

    # 3. Advanced multi-output task
    train_advanced_yield()

    # 4. Save all results
    results_path = os.path.join(MODELS_DIR, "model_evaluation_results.json")
    
    # Clean classification_report objects (they contain numpy types)
    def clean_for_json(obj):
        if isinstance(obj, dict):
            return {k: clean_for_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [clean_for_json(i) for i in obj]
        elif isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    with open(results_path, 'w') as f:
        json.dump(clean_for_json(all_results), f, indent=2)

    elapsed = time.time() - start
    print(f"\n{'='*60}")
    print(f"  ALL TRAINING COMPLETE — {elapsed:.1f}s total")
    print(f"{'='*60}")
    print(f"\n  Models saved to: {MODELS_DIR}")
    print(f"  Metrics saved to: {results_path}")

    # Summary table
    print(f"\n  {'Task':<30} {'Best Model':<15} {'Key Metric'}")
    print(f"  {'-'*60}")
    for task_name, res in all_results.items():
        if task_name == "advanced_yield":
            for sub, sres in res["sub_tasks"].items():
                best = sres["selected_best"]
                if sres["problem_type"] == "regression":
                    r2 = sres["models"][best]["test_metrics"]["r2"]
                    print(f"  adv/{sub:<26} {best:<15} R²={r2:.4f}")
                else:
                    acc = sres["models"][best]["test_metrics"]["accuracy"]
                    print(f"  adv/{sub:<26} {best:<15} Acc={acc:.4f}")
        else:
            best = res["selected_best"]
            metrics = res["models"][best]["test_metrics"]
            if res["problem_type"] == "classification":
                print(f"  {task_name:<30} {best:<15} Acc={metrics['accuracy']:.4f}")
            else:
                print(f"  {task_name:<30} {best:<15} R²={metrics['r2']:.4f}")

    print(f"\n  Generated model files:")
    for fn in sorted(os.listdir(MODELS_DIR)):
        fpath = os.path.join(MODELS_DIR, fn)
        sz = os.path.getsize(fpath)
        if sz > 1024 * 1024:
            print(f"    📦 {fn} ({sz / (1024*1024):.1f} MB)")
        elif sz > 1024:
            print(f"    📦 {fn} ({sz / 1024:.1f} KB)")
        else:
            print(f"    📦 {fn} ({sz} B)")
