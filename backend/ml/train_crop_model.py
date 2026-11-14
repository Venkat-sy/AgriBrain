#!/usr/bin/env python3

""""
Train Crop Recommendation Model with XGBoost + Hyperparameter Tuning
====================================================================
Loads the agricultural dataset, applies SMOTE for class balancing,
performs RandomizedSearchCV for hyperparameter optimization,
and exports the best model to saved_models/xgboost_crop_model.joblib
"""

import os
import json
import warnings
from pathlib import Path

import pandas as pd
import numpy as np
import joblib
from scipy.stats import uniform, randint

from sklearn.model_selection import train_test_split, RandomizedSearchCV, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

warnings.filterwarnings("ignore")

# Paths
BASE_DIR = Path(r"c:\Users\USER\Downloads\FinalYearProject")
TRAIN_DATA_DIR = BASE_DIR / "training_data"
MODEL_DIR = BASE_DIR / "models"
SAVED_MODELS_DIR = BASE_DIR / "backend" / "ml" / "saved_models"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

with open(TRAIN_DATA_DIR / "crop_label_mapping.json", "r") as f:
    LABEL_MAPPING = json.load(f)
IDX_TO_CROP = {int(v): k for k, v in LABEL_MAPPING.items()}
NUM_CLASSES = len(LABEL_MAPPING)

def load_data():
    print("Loading training data...")
    train_df = pd.read_csv(TRAIN_DATA_DIR / "crop_recommendation_train.csv")
    val_df = pd.read_csv(TRAIN_DATA_DIR / "crop_recommendation_val.csv")
    test_df = pd.read_csv(TRAIN_DATA_DIR / "crop_recommendation_test.csv")
    full_df = pd.concat([train_df, val_df, test_df], ignore_index=True)
    print(f"Total samples: {len(full_df)}")
    print(f"Class distribution:\n{full_df['label_encoded'].value_counts().sort_index()}")
    X = full_df[["feature_a", "feature_b", "feature_c"]].values
    y = full_df["label_encoded"].values
    return X, y

def main():
    print("=" * 60)
    print("Crop Recommendation Model Training with XGBoost + RandomizedSearchCV")
    print("=" * 60)
    X, y = load_data()
    scaler = StandardScaler()
    X_train_raw = pd.read_csv(TRAIN_DATA_DIR / "crop_recommendation_train.csv")[["feature_a", "feature_b", "feature_c"]].values
    scaler.fit(X_train_raw)
    X_scaled = scaler.transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    from imblearn.pipeline import Pipeline as ImbPipeline
    from imblearn.over_sampling import SMOTE
    from xgboost import XGBClassifier
    from scipy.stats import uniform, randint
    from imblearn.pipeline import Pipeline
    # Check for NaN values
    print(f"NaN in X_train: {np.isnan(X_train).sum()}")
    print(f"NaN in X_test: {np.isnan(X_test).sum()}")
    # Handle any NaN values
    if np.isnan(X_train).any() or np.isnan(X_test).any():
        from sklearn.impute import SimpleImputer
        imputer = SimpleImputer(strategy='mean')
        X_train = imputer.fit_transform(X_train)
        X_test = imputer.transform(X_test)
        print("NaN values imputed with mean")

    pipeline = Pipeline([
        ("smote", SMOTE(random_state=42, k_neighbors=3)),
        ("xgb", XGBClassifier(
            objective="multi:softprob",
            num_class=NUM_CLASSES,
            eval_metric="mlogloss",
            random_state=42,
            n_jobs=-1,
            verbosity=0
        ))
    ])
    param_dist = {
        "xgb__n_estimators": randint(100, 500),
        "xgb__max_depth": randint(3, 10),
        "xgb__learning_rate": uniform(0.01, 0.3),
        "xgb__subsample": uniform(0.6, 0.4),
        "xgb__colsample_bytree": uniform(0.6, 0.4),
        "xgb__gamma": uniform(0, 0.5),
        "xgb__min_child_weight": randint(1, 10),
        "xgb__reg_alpha": uniform(0, 1),
        "xgb__reg_lambda": uniform(0, 1),
    }
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    random_search = RandomizedSearchCV(
        estimator=pipeline,
        param_distributions=param_dist,
        n_iter=30,
        cv=5,
        scoring="accuracy",
        n_jobs=-1,
        verbose=1,
        random_state=42,
        return_train_score=True
    )
    print("\nStarting RandomizedSearchCV...")
    random_search.fit(X_train, y_train)
    best_model = random_search.best_estimator_
    best_params = random_search.best_params_
    best_cv_score = random_search.best_score_
    print(f"\n{'='*60}")
    print("BEST PARAMETERS FOUND:")
    print(f"{'='*60}")
    for param, value in best_params.items():
        print(f"  {param}: {value}")
    print(f"\nBest CV Accuracy: {best_cv_score:.4f}")
    y_pred = best_model.predict(X_test)
    test_accuracy = accuracy_score(y_test, y_pred)
    print(f"Test Accuracy: {test_accuracy:.4f}")
    print(f"\nClassification Report:")
    from sklearn.metrics import classification_report, confusion_matrix
    print(classification_report(y_test, y_pred, target_names=[IDX_TO_CROP[i] for i in sorted(IDX_TO_CROP.keys())]))
    from sklearn.metrics import confusion_matrix
    cm = confusion_matrix(y_test, y_pred)
    print(f"\nConfusion Matrix:")
    print(cm)
    import joblib
    model_path = SAVED_MODELS_DIR / "xgboost_crop_model.joblib"
    import joblib
    joblib.dump(best_model, model_path)
    print(f"\nBest model saved to: {model_path}")
    scaler_path = SAVED_MODELS_DIR / "xgboost_crop_scaler.joblib"
    joblib.dump(scaler, scaler_path)
    print(f"Scaler saved to: {scaler_path}")
    feature_info = {
        "feature_columns": ["feature_a", "feature_b", "feature_c"],
        "target_column": "label_encoded",
        "num_classes": NUM_CLASSES,
        "label_mapping": LABEL_MAPPING,
        "best_params": {k.replace("xgb__", ""): v for k, v in best_params.items()},
        "cv_accuracy": float(best_cv_score),
        "test_accuracy": float(test_accuracy),
        "model_type": "XGBClassifier",
    }
    info_path = SAVED_MODELS_DIR / "xgboost_crop_model_info.json"
    import json
    with open(info_path, "w") as f:
        json.dump(feature_info, f, indent=2)
    print(f"Model info saved to: {info_path}")
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_model, MODEL_DIR / "xgboost_crop_model.joblib")
    joblib.dump(scaler, TRAIN_DATA_DIR / "crop_scaler.pkl")
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"Best model saved to: {model_path}")
    print(f"Test Accuracy: {test_accuracy:.4f}")
    return best_model, scaler

if __name__ == "__main__":
    main()