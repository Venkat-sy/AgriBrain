"""
Stage 4: SHAP Explainability Analysis
======================================
AI-Driven Nutrient Recommendation System

Generates SHAP (SHapley Additive exPlanations) visualizations for all trained models.
Produces:
  - Summary bar plots (global feature importance)
  - Beeswarm plots (feature impact distribution)
  - Dependence plots (individual feature effects)
  - Waterfall plots (single-prediction explanations)

All plots saved to output/shap/ as high-resolution PNGs.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving figures
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

try:
    import shap
    print(f"SHAP version: {shap.__version__}")
except ImportError:
    print("ERROR: shap is not installed. Run: pip install shap")
    exit(1)

# ─── Configuration ───────────────────────────────────────────────────────────

BASE_DIR = r"c:\Users\USER\Downloads\FinalYearProject"
TRAIN_DIR = os.path.join(BASE_DIR, "training_data")
MODELS_DIR = os.path.join(BASE_DIR, "models")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "shap")
os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(os.path.join(TRAIN_DIR, "feature_config.json"), "r") as f:
    config = json.load(f)

# Style settings
plt.rcParams.update({
    'figure.dpi': 150,
    'savefig.dpi': 150,
    'savefig.bbox': 'tight',
    'font.size': 11,
})

# Use a sample of data for SHAP (speeds up computation for tree explainers)
SHAP_SAMPLE_SIZE = 500  # Max samples for SHAP values computation
BACKGROUND_SIZE = 100   # Background samples for KernelExplainer (if needed)


def load_data_and_model(task_name, model_prefix="best"):
    """Load model and test data for a task."""
    cfg = config[task_name]
    features = cfg["input_features"]

    model_path = os.path.join(MODELS_DIR, f"{model_prefix}_{task_name}_model.pkl")
    if not os.path.exists(model_path):
        return None, None, None, None

    model = joblib.load(model_path)
    test_df = pd.read_csv(os.path.join(TRAIN_DIR, f"{task_name}_test.csv"))
    X_test = test_df[features]

    target_col = cfg.get("target_column", None)
    y_test = test_df[target_col] if target_col else None

    return model, X_test, y_test, features


def generate_shap_plots(task_name, model, X_test, features, problem_type, subtitle=""):
    """Generate all SHAP plots for a given model and data."""
    tag = f"{task_name}{'_' + subtitle if subtitle else ''}"
    print(f"\n  📊 Generating SHAP plots for: {tag}")

    # Subsample for speed
    n = min(SHAP_SAMPLE_SIZE, len(X_test))
    X_sample = X_test.sample(n=n, random_state=42).reset_index(drop=True)

    # Create TreeExplainer (works for RF and XGBoost)
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_sample)
    except Exception as e:
        print(f"    ⚠ TreeExplainer failed ({e}), trying Explainer...")
        explainer = shap.Explainer(model, X_sample)
        shap_values = explainer(X_sample)

    # For multi-class classification, shap_values is a list of arrays (one per class)
    # We'll use the mean absolute SHAP values across all classes for summary
    is_multiclass = isinstance(shap_values, list) and len(shap_values) > 1

    # ── 1. Summary Bar Plot (Global Feature Importance) ──
    print("    → Summary bar plot...")
    plt.figure(figsize=(10, 6))
    if is_multiclass:
        # Stack absolute SHAP values across classes
        mean_abs = np.mean([np.abs(sv) for sv in shap_values], axis=0)
        feature_importance = np.mean(mean_abs, axis=0)
        sorted_idx = np.argsort(feature_importance)[::-1]
        plt.barh(range(len(features)), feature_importance[sorted_idx[::-1]],
                 color='#2196F3', edgecolor='#1565C0')
        plt.yticks(range(len(features)), [features[i] for i in sorted_idx[::-1]])
    else:
        if hasattr(shap_values, 'values'):
            vals = np.abs(shap_values.values)
        else:
            vals = np.abs(shap_values)
        feature_importance = np.mean(vals, axis=0)
        sorted_idx = np.argsort(feature_importance)[::-1]
        plt.barh(range(len(features)), feature_importance[sorted_idx[::-1]],
                 color='#4CAF50', edgecolor='#2E7D32')
        plt.yticks(range(len(features)), [features[i] for i in sorted_idx[::-1]])

    plt.xlabel('Mean |SHAP Value|')
    plt.title(f'Feature Importance — {task_name.replace("_", " ").title()}')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{tag}_summary_bar.png"))
    plt.close()

    # ── 2. Beeswarm Plot ──
    print("    → Beeswarm plot...")
    plt.figure(figsize=(10, 6))
    try:
        if is_multiclass:
            # For multi-class, use class 0 or mean
            shap.summary_plot(shap_values, X_sample, feature_names=features,
                              show=False, plot_size=(10, 6))
        else:
            if hasattr(shap_values, 'values'):
                shap.summary_plot(shap_values.values, X_sample, feature_names=features,
                                  show=False, plot_size=(10, 6))
            else:
                shap.summary_plot(shap_values, X_sample, feature_names=features,
                                  show=False, plot_size=(10, 6))
    except Exception as e:
        print(f"    ⚠ Beeswarm failed: {e}")
    plt.title(f'SHAP Beeswarm — {task_name.replace("_", " ").title()}')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, f"{tag}_beeswarm.png"))
    plt.close()

    # ── 3. Dependence Plots (top 3 features) ──
    print("    → Dependence plots (top 3 features)...")
    top_features_idx = sorted_idx[:3]
    for i, feat_idx in enumerate(top_features_idx):
        plt.figure(figsize=(8, 5))
        feat_name = features[feat_idx]
        try:
            if is_multiclass:
                # Use class with highest mean abs SHAP
                class_means = [np.mean(np.abs(sv[:, feat_idx])) for sv in shap_values]
                best_class = np.argmax(class_means)
                shap.dependence_plot(feat_idx, shap_values[best_class], X_sample,
                                     feature_names=features, show=False)
            else:
                sv = shap_values.values if hasattr(shap_values, 'values') else shap_values
                shap.dependence_plot(feat_idx, sv, X_sample,
                                     feature_names=features, show=False)
        except Exception as e:
            print(f"    ⚠ Dependence plot for {feat_name} failed: {e}")
            plt.close()
            continue
        plt.title(f'SHAP Dependence: {feat_name} — {task_name.replace("_", " ").title()}')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{tag}_dependence_{feat_name}.png"))
        plt.close()

    # ── 4. Waterfall Plot (single prediction explanation) ──
    print("    → Waterfall plot (sample prediction)...")
    try:
        # Re-compute for a single sample using Explainer for waterfall compatibility
        single_explainer = shap.Explainer(model, X_sample)
        single_sv = single_explainer(X_sample.iloc[:1])
        plt.figure(figsize=(10, 6))
        shap.plots.waterfall(single_sv[0], show=False)
        plt.title(f'Single Prediction Explanation — {task_name.replace("_", " ").title()}')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, f"{tag}_waterfall.png"))
        plt.close()
    except Exception as e:
        print(f"    ⚠ Waterfall plot failed: {e}")

    print(f"    ✅ All SHAP plots saved for {tag}")


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  STAGE 4: SHAP EXPLAINABILITY ANALYSIS")
    print("  AI-Driven Nutrient Recommendation System")
    print("=" * 60)

    # 1. Main classification tasks
    for task_name in ["crop_recommendation", "fertilizer_recommendation"]:
        model, X_test, y_test, features = load_data_and_model(task_name)
        if model is None:
            print(f"\n  ⚠ Skipping {task_name} — model not found")
            continue
        generate_shap_plots(task_name, model, X_test, features, "classification")

    # 2. Yield prediction (regression)
    model, X_test, y_test, features = load_data_and_model("yield_prediction")
    if model is not None:
        generate_shap_plots("yield_prediction", model, X_test, features, "regression")
    else:
        print("\n  ⚠ Skipping yield_prediction — model not found")

    # 3. Advanced yield sub-tasks
    adv_cfg = config["advanced_yield"]
    adv_features = adv_cfg["input_features"]
    adv_targets = [
        ("Yield_tons_per_ha", "regression"),
        ("Irrigation_Demand_mm", "regression"),
        ("Crop_Failure_Risk", "classification"),
    ]

    for target, ptype in adv_targets:
        model_path = os.path.join(MODELS_DIR, f"best_adv_{target}_model.pkl")
        if not os.path.exists(model_path):
            print(f"\n  ⚠ Skipping adv/{target} — model not found")
            continue

        model = joblib.load(model_path)
        test_df = pd.read_csv(os.path.join(TRAIN_DIR, "advanced_yield_test.csv"))
        X_test = test_df[adv_features]
        generate_shap_plots(f"advanced_{target}", model, X_test, adv_features, ptype)

    # Summary
    print(f"\n{'='*60}")
    print(f"  SHAP ANALYSIS COMPLETE")
    print(f"{'='*60}")
    print(f"\n  All plots saved to: {OUTPUT_DIR}")
    print(f"\n  Generated files:")
    for fn in sorted(os.listdir(OUTPUT_DIR)):
        sz = os.path.getsize(os.path.join(OUTPUT_DIR, fn))
        print(f"    🖼 {fn} ({sz / 1024:.1f} KB)")
