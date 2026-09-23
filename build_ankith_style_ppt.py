"""
AI-Driven Digital Twin Framework — Plain Text PPT
Style: Minimal handwritten outline. White background. No tables. No shapes.
Just title + body text in default placeholders.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

BLUE_TITLE   = RGBColor(0, 102, 204)
GREEN        = RGBColor(34, 139, 34)
BLACK        = RGBColor(0, 0, 0)

prs = Presentation()
prs.slide_width  = Inches(10)
prs.slide_height = Inches(7.5)


def _font(p, size=13, bold=False, italic=False, color=BLACK, align=PP_ALIGN.LEFT):
    p.font.size = Pt(size)
    p.font.bold = bold
    p.font.italic = italic
    p.font.color.rgb = color
    p.font.name = "Calibri"
    p.alignment = align


def add_content_slide(title_text, body_text):
    """Plain content slide — title (blue) + body (black) in default placeholders."""
    slide = prs.slides.add_slide(prs.slide_layouts[1])

    # Title
    ts = slide.shapes.title
    ts.text = title_text
    _font(ts.text_frame.paragraphs[0], size=20, bold=True, color=BLUE_TITLE)

    # Body — set whole text, then style first paragraph (the only existing one)
    bs = slide.placeholders[1]
    bs.text_frame.text = body_text
    for para in bs.text_frame.paragraphs:
        _font(para, size=13, color=BLACK)
    return slide


# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 1 — Title
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(prs.slide_layouts[0])
ts = s.shapes.title
ts.text = "AI-Driven Digital Twin Framework for Sustainable Agriculture"
_font(ts.text_frame.paragraphs[0], size=26, bold=True, color=GREEN,
      align=PP_ALIGN.CENTER)

sub = s.placeholders[1]
sub.text_frame.text = (
    "A What-If Simulation System for Crop Yield, Irrigation, and Risk Assessment\n\n"
    "Presented By: K. Venkatesh Hebbar\n"
    "Guide: Mr. Krishna Prasad D S\n"
    "Project Coordinator: Dr. Radhakrishna\n"
    "Department of Computer and Communication Engineering\n"
    "NMAM Institute of Technology, Nitte\n\n"
    "September 2026"
)
for para in sub.text_frame.paragraphs:
    _font(para, size=14, color=BLACK, align=PP_ALIGN.CENTER)
print("  Slide 1")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 2
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Introduction: Digital Agriculture",
    "Context:\n"
    "Agriculture supports 58% of India's population and 86% of farms are smaller "
    "than 2 hectares. These smallholders face increasing climate unpredictability, "
    "soil degradation, and water scarcity. 80% of India's freshwater is used in "
    "farming and 40% is wasted through imprecise irrigation.\n\n"
    "Challenge:\n"
    "Traditional advisory systems deliver static, region-level recommendations that "
    "ignore field-level soil variation and sensor drift. Black-box AI predictions "
    "without explanations are routinely rejected by farmers who cannot understand "
    "why a recommendation is being made.\n\n"
    "Goal:\n"
    "Build a unified AI + Digital Twin + XAI platform that predicts crop yield, "
    "irrigation demand, and climate risk — then lets farmers test what-if scenarios "
    "on a virtual replica of their field before committing real resources."
)
print("  Slide 2")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 3
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Alignment with UN Sustainable Development Goals",
    "UN SDG 2 — Zero Hunger:\n"
    "Improve crop yield prediction accuracy to reduce losses and increase food output.\n\n"
    "UN SDG 6 — Clean Water and Sanitation:\n"
    "Drive precision irrigation to cut agricultural water use by 15–30%.\n\n"
    "UN SDG 12 — Responsible Consumption and Production:\n"
    "Optimize fertilizer application through data-driven soil NPK analysis.\n\n"
    "UN SDG 13 — Climate Action:\n"
    "Provide early-warning risk prediction and scenario simulation for climate shocks.\n\n"
    "UN SDG 11 — Sustainable Cities and Communities:\n"
    "Build accessible, low-cost advisory dashboards for rural smallholders."
)
print("  Slide 3")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 4
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Literature Survey: Algorithms and Methods",
    "1. Deep Learning + SHAP for Crop Yield [2023 — Nature]\n"
    "   Key Finding: Deep models with SHAP produce transparent predictions.\n"
    "   Limitation: High inference cost; SHAP is expensive on deep architectures.\n\n"
    "2. Lightweight Edge ML for Sensor-Based Agriculture [2023 — Springer]\n"
    "   Key Finding: On-device inference removes cloud dependency.\n"
    "   Limitation: Single model — no reliability guarantee or fallback.\n\n"
    "3. Hybrid ML — Random Forest + XGBoost for Tabular Farm Data [2024 — Elsevier]\n"
    "   Key Finding: Ensemble methods outperform single classifiers on soil data.\n"
    "   Limitation: No what-if simulation; static point predictions only.\n\n"
    "4. Agentic AI for Autonomous Farm Decision Support [2025 — Frontiers]\n"
    "   Key Finding: Autonomous agents can act on sensor streams.\n"
    "   Limitation: Requires expensive orchestration; opaque decisions.\n\n"
    "5. Feature Correlation KNN for Soil Variable Isolation [2026 — IEEE]\n"
    "   Key Finding: KNN identifies the most impactful soil features.\n"
    "   Limitation: Descriptive only; no predictive model."
)
print("  Slide 4")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 5
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Literature Survey: Universal Limitations",
    "1. Black-Box Predictions [2023–2024 Nature papers]\n"
    "   Finding: Most models produce raw numeric outputs with no explanation.\n"
    "   Impact: Farmers cannot trust AI outputs they do not understand.\n\n"
    "2. Sensor Drift Decay [2026 IoT-ML evaluation]\n"
    "   Finding: Real sensors degrade over months, silently dropping accuracy.\n"
    "   Impact: Models trained on clean data become unreliable over time.\n\n"
    "3. Unstructured Climate Data [2024 Hybrid ML paper]\n"
    "   Finding: Erratic weather and missing values break hybrid pipelines.\n"
    "   Impact: No graceful handling of broken or sparse inputs.\n\n"
    "4. No What-If Testing [All surveyed papers]\n"
    "   Finding: Every system gives one prediction per input — no scenario exploration.\n"
    "   Impact: Farmers cannot stress-test recommendations before acting.\n\n"
    "5. Static Region-Level Recommendations [Across all papers]\n"
    "   Finding: Advisory systems ignore field-level soil and microclimate variation.\n"
    "   Impact: Recommendations are too coarse for precision farming."
)
print("  Slide 5")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 6
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Research Gap Matrix: Literature vs Proposed System",
    "Capability                          | Existing Literature  | Proposed System\n"
    "------------------------------------|----------------------|----------------------\n"
    "Crop Yield Prediction               | Yes (partial)        | Yes (RF + XGBoost)\n"
    "Irrigation Prediction              | No                   | Yes (Decision Tree)\n"
    "Climate Risk Classification        | Partial (2-tier)    | Yes (3-tier)\n"
    "SHAP-based Explainability            | Partial (post-hoc)   | Yes (per-prediction)\n"
    "IoT Sensor Integration              | Yes                  | Yes (MQTT-ready)\n"
    "Digital Twin Simulation             | No                   | Yes (Novel)\n"
    "Interactive What-If Dashboard       | No                   | Yes (Glassmorphism SPA)\n"
    "Scenario Stress-Testing             | No                   | Yes (response < 2 s)\n"
    "Multi-Output Prediction             | Rare                 | Yes (yield + irr + risk)\n\n"
    "Key Insight: Existing systems are 'predict-only' black boxes. This project is "
    "the first to combine prediction + simulation + transparent explanation in one "
    "unified platform."
)
print("  Slide 6")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 7
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Project Objectives",
    "O1 — Crop Yield Prediction:\n"
    "Build accurate regression models (Random Forest + XGBoost ensemble) for yield "
    "forecasting using soil NPK, pH, moisture, temperature, humidity, and rainfall.\n\n"
    "O2 — Irrigation Prediction:\n"
    "Estimate optimal water usage from soil moisture deficit and 7-day weather "
    "forecasts to reduce agricultural water waste by 15–30%.\n\n"
    "O3 — Agricultural Risk Prediction:\n"
    "Classify climate and environmental risk (Low / Medium / High) with probabilistic "
    "confidence for early warning and contingency planning.\n\n"
    "O4 — Digital Twin Simulation Engine (Novel Contribution):\n"
    "Build a localized virtual replica of the farm to enable what-if scenario testing "
    "before committing real resources (water, fertilizer, labor).\n\n"
    "O5 — Explainable AI Dashboard:\n"
    "Deliver a farmer-friendly glassmorphism SPA with SHAP explanations for every "
    "individual prediction, enabling transparent, trustworthy decision support."
)
print("  Slide 7")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 8
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Objective-to-Literature Mapping",
    "O1 — Yield Prediction:\n"
    "Supporting: 2023 DL+SHAP, 2024 Hybrid ML papers.\n"
    "Extension: Multi-output regression with uncertainty bounds, not single point estimate.\n\n"
    "O2 — Irrigation Prediction:\n"
    "Supporting: Critical gap — no surveyed paper addresses this for Indian smallholder farms.\n"
    "Extension: First implementation combining moisture, temperature, humidity, and 7-day rainfall.\n\n"
    "O3 — Risk Prediction:\n"
    "Supporting: 2023 Edge ML, 2025 Spatial ML.\n"
    "Extension: Combines climate anomalies + sensor drift + emission factors into one classifier.\n\n"
    "O4 — Digital Twin (Novel):\n"
    "Supporting: Not addressed in any surveyed paper.\n"
    "Extension: Virtual farm replica with explicit penalty functions and scenario routing.\n\n"
    "O5 — XAI Dashboard:\n"
    "Supporting: 2023 SHAP, 2024 XAI Hybrid.\n"
    "Extension: Real-time browser interface with per-prediction waterfall + NPK sliders."
)
print("  Slide 8")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 9
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Dataset Overview",
    "Source:\n"
    "Custom 10,000-row synthetic Indian agricultural dataset combined with Government "
    "Soil Health Card (SHC) reference data from ICAR.\n\n"
    "Crops Covered (22 varieties):\n"
    "Paddy, Wheat, Maize, Ragi, Bajra, Jowar, Cotton, Sugarcane, Groundnut, Soybean, "
    "Mustard, Sunflower, Tur Dal, Urad Dal, Green Gram, Black Gram, Sesame, Jute, "
    "Tobacco, Tea, Coffee, Rubber.\n\n"
    "Input Features (10):\n"
    "Nitrogen (kg/ha), Phosphorus (kg/ha), Potassium (kg/ha), pH, Moisture (%), "
    "Rainfall (mm), Temperature (°C), Humidity (%), Crop Type (categorical), "
    "Water Usage (L).\n\n"
    "Target Variables (3):\n"
    "Yield (tons/ha), Irrigation Demand (L), Crop Failure Risk (Low / Medium / High).\n\n"
    "Splits: 8,000 train / 1,000 validation / 1,000 test (stratified by crop type)."
)
print("  Slide 9")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 10
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Feature Engineering and Data Schema",
    "F1  Nitrogen     | kg/ha | 0–200    | Numeric     | Soil primary macronutrient\n"
    "F2  Phosphorus   | kg/ha | 0–150    | Numeric     | Soil secondary macronutrient\n"
    "F3  Potassium    | kg/ha | 0–250    | Numeric     | Soil tertiary macronutrient\n"
    "F4  pH           | —     | 3.5–9.5  | Numeric     | Soil acidity / alkalinity\n"
    "F5  Moisture     | %     | 5–95     | Numeric     | Volumetric soil water\n"
    "F6  Rainfall     | mm    | 50–3000  | Numeric     | Seasonal precipitation\n"
    "F7  Temperature  | °C    | 10–45    | Numeric     | Mean growing-season temp\n"
    "F8  Humidity     | %     | 20–100   | Numeric     | Ambient relative humidity\n"
    "F9  Crop Type    | —     | 22 cats  | Categorical | One-hot encoded\n"
    "F10 Water Usage  | L     | 0–5000   | Numeric     | Historical irrigation volume\n\n"
    "Preprocessing: Median imputation, IQR outlier capping, StandardScaler (mean=0, std=1), "
    "VIF multicollinearity check (VIF > 5 dropped)."
)
print("  Slide 10")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 11
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Data Preprocessing Pipeline",
    "Step 1 — Load Raw Datasets:\n"
    "Combine 5 Kaggle + ICAR sources into a unified 10,000-row DataFrame.\n\n"
    "Step 2 — Drop Metadata Columns:\n"
    "Remove index, timestamp, and source-specific identifier fields.\n\n"
    "Step 3 — Handle Missing Values:\n"
    "Apply median imputation for numeric fields.\n\n"
    "Step 4 — Remove Duplicates:\n"
    "Drop duplicate sensor readings.\n\n"
    "Step 5 — Outlier Treatment:\n"
    "IQR-based capping — retain edge cases as potential crop stress signals.\n\n"
    "Step 6 — Feature Engineering:\n"
    "Derive NPK balance ratio, moisture deficit, rainfall deviation from seasonal mean.\n\n"
    "Step 7 — Encoding and Scaling:\n"
    "One-hot encode crop type; StandardScaler on all numeric features.\n\n"
    "Step 8 — Multicollinearity Check:\n"
    "Variance Inflation Factor (VIF) analysis — drop features with VIF > 5."
)
print("  Slide 11")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 12
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "AI Model Training Pipeline",
    "Models Trained:\n\n"
    "Random Forest (Regression):\n"
    "n_estimators=200, max_depth=12, min_samples_leaf=4\n"
    "Inference: 12 ms | SHAP: Yes\n\n"
    "XGBoost (Regression + Classification):\n"
    "learning_rate=0.05, n_estimators=300, max_depth=8\n"
    "Inference: 8 ms | SHAP: Yes | Selected as best model\n\n"
    "Decision Tree (Irrigation Sub-Model):\n"
    "max_depth=10, min_samples_split=20\n"
    "Inference: 3 ms | SHAP: Yes\n\n"
    "Baselines (from literature):\n"
    "Deep Learning [2023]: 450 ms inference, limited SHAP\n"
    "SVM RBF [2023]: 95 ms inference, no SHAP\n\n"
    "Selection Criterion:\n"
    "Regression — highest validation R²\n"
    "Classification — highest validation F1 (macro)\n\n"
    "Saved: models/best_<task>_model.pkl + model_evaluation_results.json"
)
print("  Slide 12")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 13
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Proposed System Architecture",
    "End-to-End Flow:\n"
    "Soil Sensors + Weather API --> Preprocessing --> [RF | XGBoost] Inference\n"
    "--> Yield / Irrigation / Risk Output --> Digital Twin Engine\n"
    "--> SHAP Explainer --> Glassmorphism Dashboard --> Farmer Decision\n\n"
    "Layer 1 — Data Layer:\n"
    "Synthetic 10K-row dataset + IoT sensor stream + weather API.\n\n"
    "Layer 2 — Processing Layer:\n"
    "Cleaning, EDA, feature engineering, VIF check, StandardScaler.\n\n"
    "Layer 3 — Intelligence Layer:\n"
    "Random Forest + XGBoost — best model selected per task on validation.\n\n"
    "Layer 4 — Simulation Layer (Novel):\n"
    "Digital Twin applies explicit penalty functions (N=0.20, P=0.10, K=0.10, "
    "pH=0.15, T=0.15, Rain=0.30) with 95% yield-loss cap.\n\n"
    "Layer 5 — Presentation Layer:\n"
    "Glassmorphism SPA with sidebar tabs, real-time gauges, SHAP waterfall charts."
)
print("  Slide 13")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 14
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Digital Twin Simulation Engine (Novel Contribution)",
    "Penalty Functions:\n\n"
    "Nitrogen deficiency penalty   = 0.20  (multiplied into base yield)\n"
    "Phosphorus deficiency penalty = 0.10  (multiplied into base yield)\n"
    "Potassium deficiency penalty  = 0.10  (multiplied into base yield)\n"
    "pH imbalance penalty         = 0.15  (multiplied into base yield)\n"
    "Temperature stress penalty    = 0.15  (multiplied into base yield)\n"
    "Rainfall deficit penalty     = 0.30  (highest weight)\n"
    "Cumulative cap               = 0.95  (maximum combined yield loss)\n\n"
    "Irrigation Demand:\n"
    "Demand = max(0, (target_moisture - current_moisture) x field_area x crop_kc)\n"
    "where kc is the crop coefficient (rice=1.2, wheat=0.95, cotton=1.15).\n\n"
    "Risk Classification:\n"
    "HIGH   — cumulative penalty > 0.60 OR irrigation demand above threshold\n"
    "MEDIUM — cumulative penalty > 0.30\n"
    "LOW    — all parameters within optimal range\n\n"
    "Example: What if rainfall drops 30%? --> Twin reduces yield by 9% (0.30 x 0.30)."
)
print("  Slide 14")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 15
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Methodology: Seven-Phase Lifecycle",
    "Phase 1 — Data Collection:\n"
    "5 Kaggle + ICAR sources combined; Government Soil Health Card data integrated.\n\n"
    "Phase 2 — Preprocessing:\n"
    "Imputation, outlier capping, feature engineering, StandardScaler, VIF check.\n\n"
    "Phase 3 — Model Development:\n"
    "Random Forest + XGBoost + Decision Tree trained with GridSearchCV (cv=3).\n\n"
    "Phase 4 — Evaluation:\n"
    "Stratified k-fold validation; RMSE/MAE/R² for regression; F1/AUC for classification.\n\n"
    "Phase 5 — Digital Twin Implementation:\n"
    "Python simulation engine with explicit penalty functions and scenario routing.\n\n"
    "Phase 6 — SHAP Explainability:\n"
    "TreeExplainer for global feature importance + per-prediction waterfall charts.\n\n"
    "Phase 7 — Dashboard and Deployment:\n"
    "Glassmorphism static SPA in frontend/; CI/CD via GitHub Actions to GitHub Pages."
)
print("  Slide 15")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 16
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Benchmark Results",
    "Held-Out Test Set Performance (2,000 samples):\n\n"
    "XGBoost (ours)             | Accuracy: 0.87 | F1: 0.84 | R2: 0.85 | RMSE: 1.42 | 8 ms  | SHAP: Yes\n"
    "Random Forest (ours)        | Accuracy: 0.82 | F1: 0.79 | R2: 0.76 | RMSE: 1.85 | 12 ms | SHAP: Yes\n"
    "Deep Learning [2023]        | Accuracy: 0.85 | F1: 0.82 | R2: 0.80 | RMSE: 1.58 | 450 ms| SHAP: Limited\n"
    "SVM RBF [2023]              | Accuracy: 0.79 | F1: 0.75 | R2: 0.68 | RMSE: 2.10 | 95 ms | SHAP: No\n\n"
    "XGBoost selected as the best model for all three tasks.\n\n"
    "Digital Twin and Dashboard Performance:\n"
    "Scenario simulation response time : < 2 seconds\n"
    "SHAP waterfall generation time  : < 200 ms per prediction\n"
    "Dashboard initial load          : < 1.5 seconds\n"
    "NPK slider recompute            : < 100 ms\n"
    "Total dashboard bundle size     : ~ 180 KB (minified HTML + CSS, no JS framework)"
)
print("  Slide 16")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 17
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Dashboard and Explainable AI (XAI)",
    "Tab 1 — Overview:\n"
    "High-level farm status: yield, irrigation, risk, weather summary. "
    "3-tier color-coded risk badge (Green / Amber / Red).\n\n"
    "Tab 2 — Field Status:\n"
    "Real-time gauges for N, P, K, pH, Moisture, Temperature, Humidity. "
    "Each gauge shows current value vs optimal range.\n\n"
    "Tab 3 — AI Analytics:\n"
    "Model performance summary (accuracy, R2, RMSE), SHAP global feature importance "
    "bar chart, per-prediction SHAP waterfall chart.\n\n"
    "Tab 4 — Digital Twin (Novel):\n"
    "Interactive NPK sliders. User adjusts any input and the twin recomputes "
    "yield, irrigation demand, and risk in under 2 seconds.\n\n"
    "Tab 5 — Settings:\n"
    "Crop type, field area, target moisture threshold, language preference.\n\n"
    "Example: 'Predicted yield is 2.8 t/ha. Largest negative: pH (-0.6 t/ha). "
    "Largest positive: Nitrogen (+0.4 t/ha).'"
)
print("  Slide 17")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 18
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Project Status and Progress",
    "COMPLETED:\n"
    "Literature Survey            | 12 papers analyzed across 4 thematic groups\n"
    "Research Gap Analysis        | Gap matrix with 9 capability comparisons\n"
    "Dataset Generation           | 10,000-row synthetic Indian agricultural dataset\n"
    "EDA and Visualization       | Distribution + correlation charts in output/\n"
    "Preprocessing Pipeline       | task-specific train/val/test CSVs + feature_config.json\n"
    "Model Training               | RF + XGBoost + Decision Tree with GridSearchCV\n"
    "SHAP Explainer Integration  | Beeswarm, dependence, waterfall plots in output/shap/\n"
    "Digital Twin Engine          | Scenario routing with penalty functions\n"
    "Glassmorphism Dashboard      | frontend/index.html deployed to GitHub Pages\n\n"
    "IN PROGRESS:\n"
    "End-to-End Integration Test  | Frontend-backend smoke test, edge-case validation\n\n"
    "PLANNED:\n"
    "Real-Time IoT Deployment     | MQTT on Raspberry Pi / ESP32\n"
    "Cloud Deployment            | AWS / GCP hosting with autoscaling\n"
    "Mobile PWA                  | Offline-capable field interface, regional languages"
)
print("  Slide 18")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 19
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Future Scope and Long-Term Extensions",
    "F1 — Real-Time IoT Sensors:\n"
    "Replace synthetic data with live-streaming soil sensors via MQTT on "
    "Raspberry Pi / ESP32.\n\n"
    "F2 — Satellite and Drone Imagery:\n"
    "Add NDVI vegetation index and drone-based pest detection to enrich the feature set.\n\n"
    "F3 — Mobile PWA (Regional Languages):\n"
    "Offline-capable Progressive Web App for low-literacy farmers "
    "(Kannada, Hindi, Tamil, Telugu).\n\n"
    "F4 — Reinforcement Learning Agent:\n"
    "Self-optimizing agent learning from seasonal outcomes "
    "(reward = yield - input cost).\n\n"
    "F5 — Smart Farm Automation:\n"
    "Direct valve actuation for precise drip irrigation control with manual override safety.\n\n"
    "F6 — Multi-Region Generalization:\n"
    "Region-specific models for distinct agro-climatic zones of India "
    "(arid, semi-arid, sub-humid, humid, coastal).\n\n"
    "F7 — Carbon-Footprint Tracking:\n"
    "Estimate CO2 equivalent savings from reduced fertilizer and water use for ESG reporting."
)
print("  Slide 19")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 20
# ─────────────────────────────────────────────────────────────────────────────
add_content_slide(
    "Expected Results and Project Impact",
    "R1 — Improved Yield Prediction:\n"
    "Target: ±10% error vs baseline 25%. Maps to Objective O1. Impact: higher food output.\n\n"
    "R2 — Water Conservation:\n"
    "Target: 15–30% water savings. Maps to Objective O2. Impact: SDG 6 — freshwater scarcity.\n\n"
    "R3 — Early Risk Detection:\n"
    "Target: 48-hour advance warning. Maps to Objective O3. Impact: lower crop failure rate.\n\n"
    "R4 — Scenario Simulation Speed:\n"
    "Target: < 2 seconds response time. Maps to Objective O4. Impact: real-time what-if experience.\n\n"
    "R5 — Sustainable Farming Alignment:\n"
    "Target: Soil health + 4 SDGs. Maps to Objectives O1–O5. Impact: long-term ecosystem health.\n\n"
    "Combined Impact (10,000-farmer adoption estimate):\n"
    "1.5–3.0 billion liters of water saved annually, 20% reduction in fertilizer "
    "over-application, actionable early warnings to 80% of subscribed farms within "
    "first two growing seasons."
)
print("  Slide 20")

# ─────────────────────────────────────────────────────────────────────────────
# SLIDE 21 — Conclusion
# ─────────────────────────────────────────────────────────────────────────────
s = prs.slides.add_slide(prs.slide_layouts[1])
ts = s.shapes.title
ts.text = "Conclusion and Thank You"
_font(ts.text_frame.paragraphs[0], size=20, bold=True, color=GREEN)

bs = s.placeholders[1]
bs.text_frame.text = (
    "Enabling Sustainable Indian Agriculture through\n"
    "AI-Driven Digital Twin + Explainable Machine Learning.\n\n"
    "Three Pillars:\n\n"
    "PREDICT  — Accurate yield, irrigation, and risk forecasts using RF + XGBoost ensemble.\n\n"
    "SIMULATE — What-if scenarios on a Digital Twin replica of the farm before committing resources.\n\n"
    "EXPLAIN  — Transparent SHAP explanations for every individual prediction a farmer receives.\n\n"
    "Thank You!"
)
for para in bs.text_frame.paragraphs:
    _font(para, size=18, color=BLACK, align=PP_ALIGN.CENTER)
print("  Slide 21")

# ─────────────────────────────────────────────────────────────────────────────
# Save
# ─────────────────────────────────────────────────────────────────────────────
output_path = r"C:\Users\USER\Downloads\FinalYearProject\Venkatesh_Plain_PPT.pptx"
prs.save(output_path)
print()
print(f"Saved: {output_path}")
print(f"Slides: {len(prs.slides)}")
