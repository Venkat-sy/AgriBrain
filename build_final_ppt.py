from pptx import Presentation
from pptx.util import Inches, Pt
import os

prs = Presentation()

def create_slide(title, content_list=None):
    slide_layout = prs.slide_layouts[1]
    slide = prs.slides.add_slide(slide_layout)
    title_box = slide.shapes.title
    title_box.text = title
    
    if content_list:
        body_shape = slide.shapes.placeholders[1]
        tf = body_shape.text_frame
        for item in content_list:
            p = tf.add_paragraph()
            p.text = item
            p.level = 0
            p.font.size = Pt(18)
    return slide

# Slide 1: Title
slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "AI-Driven Digital Twin Framework for Sustainable Agriculture"
subtitle.text = "A What-If Simulation System for Crop Yield, Irrigation, and Risk Assessment\n\nStudent: K. Venkatesh Hebbar\nGuide: Mr. Krishna Prasad D S\nProject Coordinator: Dr. Radhakrishna"

# Slide 2: Introduction
create_slide("Introduction: Digital Agriculture", [
    "Digital Agriculture is the integration of advanced technologies (AI, IoT) into farming.",
    "It transforms traditional, intuition-based farming into highly precise, data-driven science.",
    "Our project perfectly aligns with the United Nations Sustainable Development Goals (SDGs):",
    "  - SDG 2: Zero Hunger (Optimizing crop yields)",
    "  - SDG 6: Clean Water and Sanitation (Intelligent irrigation)",
    "  - SDG 12: Responsible Consumption and Production (Precise fertilizer use)",
    "  - SDG 13: Climate Action (Climate-resilient risk prediction)"
])

# Slide 3: Literature Survey - Methods & Algorithms
create_slide("Literature Survey: Methodologies & Algorithms", [
    "Analyzed recent, verified Journal/Transaction papers (2023-2026).",
    "Algorithms Evaluated:",
    "  - Deep Learning + SHAP (High accuracy, transparent, but needs large datasets).",
    "  - Lightweight Edge ML (Real-time, local processing, limited by compute power).",
    "  - Hybrid ML (Random Forest, XGBoost) combined with Explainable AI.",
    "  - Agentic AI & Decision Trees (Autonomous but high setup complexity).",
    "  - Feature Correlation KNN (Isolates impactful variables but computationally heavy)."
])

# Slide 4: Literature Survey - Limitations & Problems
create_slide("Literature Survey: Current Limitations", [
    "Current agricultural ML systems act as strict 'Predict Only' tools.",
    "Major Flaws Identified in Literature:",
    "  - Hardware degradation: 'Sensor drift' causes long-term ML accuracy decay (2026).",
    "  - Unstructured Data: Hybrid models struggle significantly with erratic meteorological anomalies (2024).",
    "  - Scalability: Cloud-based models face extreme latency in rural areas.",
    "  - The 'Black Box' Barrier: Farmers reject unexplained AI recommendations."
])

# Slide 5: Literature Survey - Our Proposed Solution
create_slide("Literature Survey: Proposed Solution", [
    "To overcome the 'Predict Only' limitation, we introduce:",
    "  1. Digital Twin Simulation: A virtual replica to test 'What-If' scenarios (e.g., 'What if rainfall drops 20%?').",
    "  2. Explainable AI (SHAP): Translates complex AI decisions into human-readable insights to build farmer trust.",
    "This transitions the paradigm from reactive prediction to proactive simulation."
])

# Slide 6: Research Gap Analysis
create_slide("Research Gap Analysis", [
    "Existing Research: Provides highly accurate, but static, 'One-Size-Fits-All' recommendations.",
    "Findings: ML models can predict yields, but lack transparency and dynamic simulation.",
    "Limitations: Systems cannot answer hypothetical questions or simulate changing environments.",
    "Missing Features: Dynamic scenario testing, transparent logic interfaces, Digital Twin representation.",
    "Final Gap: There is a critical need to transition from a rigid 'Predict Only' paradigm to a resilient, transparent 'Predict + Simulate Future Scenarios' framework."
])

# Slide 7: Project Objectives
create_slide("Project Objectives", [
    "1. Develop an AI-based crop yield prediction model using environmental and soil parameters.",
    "2. Design an intelligent irrigation prediction model for efficient water management.",
    "3. Develop a crop risk prediction module to estimate agricultural risks under varying climates.",
    "4. Implement a Digital Twin simulation engine for interactive 'what-if' scenario analysis.",
    "5. Build an Explainable AI (SHAP) dashboard that provides transparent decision support."
])

# Slide 8: Objective Mapping (Year & Literature)
create_slide("Objective Mapping to Literature", [
    "Obj 1 (Yield Prediction): Supported by 2023 (DL+SHAP) and 2024 (Hybrid ML) papers. Solves static NPK calculations.",
    "Obj 2 (Irrigation Prediction): Addresses the critical gap in localized water management tools.",
    "Obj 3 (Risk Prediction): Supported by 2023 & 2024 papers on climate resilience and weather anomalies.",
    "Obj 4 (Digital Twin): Solves the 'Predict Only' limitation identified across all surveyed literature.",
    "Obj 5 (XAI Dashboard): Directly solves the 'Black Box' trust barrier noted in 2023 & 2024 research."
])

# Slide 9: Dataset Table
create_slide("Dataset Details", [
    "Synthetic/Advanced Indian Soil Health Data (10,000 rows):",
    "  - Source: Custom Generation + Government Portals (Soil Health Cards).",
    "  - Objective: Trains Yield, Irrigation, and Risk models.",
    "  - Year: Baseline data curated for 2026 execution.",
    "Features Extracted:",
    "  - Soil: Nitrogen (N), Phosphorus (P), Potassium (K), pH, Moisture.",
    "  - Weather: Rainfall, Temperature, Humidity.",
    "  - Farm: Crop Type, Water Usage."
])

# Slide 10: Proposed Workflow
create_slide("Proposed Workflow", [
    "1. Data Collection (IoT / SHC Data)",
    "2. Data Cleaning (Imputation / Outlier Removal)",
    "3. Preprocessing (Standard Scaling / Encoding)",
    "4. Feature Engineering (Multicollinearity Checks)",
    "5. Model Training (Random Forest / XGBoost)",
    "6. Prediction Modules (Yield, Irrigation, Risk)",
    "7. Digital Twin (Scenario Routing)",
    "8. Explainable AI (SHAP Analysis)",
    "9. Dashboard (Glassmorphism UI) -> Decision Support"
])

# Slide 11: System Architecture (with image)
arch_slide_layout = prs.slide_layouts[5]  # blank layout
arch_slide = prs.slides.add_slide(arch_slide_layout)

# Add title text box at top
from pptx.util import Emu
title_txBox = arch_slide.shapes.add_textbox(Inches(0.3), Inches(0.1), Inches(9.4), Inches(0.7))
title_tf = title_txBox.text_frame
title_p = title_tf.paragraphs[0]
title_p.text = "System Architecture"
title_p.font.size = Pt(28)
title_p.font.bold = True

# Embed architecture image, centered and scaled to fit slide
arch_img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "system_architecture.jpg")
if os.path.exists(arch_img_path):
    arch_slide.shapes.add_picture(arch_img_path, Inches(1.8), Inches(0.85), Inches(6.0), Inches(6.5))
else:
    # Fallback to text if image not found
    tb = arch_slide.shapes.add_textbox(Inches(0.5), Inches(1.0), Inches(9.0), Inches(5.5))
    tf2 = tb.text_frame
    tf2.word_wrap = True
    lines = [
        "Agricultural Dataset: Soil Data, Weather Data, Crop Data, Historical Yield",
        "Data Cleaning & EDA: Missing Value Handling, Outlier Detection, Correlation Analysis",
        "Yield Prediction Model | Irrigation Prediction Model | Risk Prediction Model",
        "Digital Twin Simulation Engine: What-if Modeling, Crop Growth Simulation",
        "Scenario Analysis Dashboard: Interactive Visualizations, KPI Monitoring",
        "Decision Support System: Actionable Recommendations, Resource Optimization"
    ]
    for line in lines:
        lp = tf2.add_paragraph()
        lp.text = line
        lp.font.size = Pt(16)

# Slide 12: Digital Twin Concept
create_slide("Digital Twin Concept", [
    "Physical Farm: Tangible Crops, Soil, Sensors, Irrigation, and Weather.",
    "Digital Twin: The Virtual Farm Replica.",
    "Functions: Real-Time Monitoring, Analytics, Simulation, Predictions, Decision Support.",
    "Continuous Feedback Loop:",
    "  Physical Farm ↔ Sensors ↔ Data Stream ↔ Digital Twin ↔ AI Models ↔ Recommendations ↔ Physical Farm"
])

# Slide 13: Crop Yield Prediction Module
create_slide("Module 1: Crop Yield Prediction", [
    "Inputs: Nitrogen, Phosphorus, Potassium, pH, Crop Type, Historic Weather.",
    "Algorithms: Random Forest, XGBoost (Tree-based for XAI compatibility).",
    "Outputs: Expected Yield (Tons/Hectare).",
    "Metrics: RMSE, R-squared Score, MAE.",
    "Contribution to Twin: Projects final harvest based on simulated soil degradation."
])

# Slide 14: Irrigation Prediction Module
create_slide("Module 2: Irrigation Prediction", [
    "Inputs: Soil Moisture, Temperature, Humidity, Rainfall Forecast.",
    "Algorithms: Decision Trees, Random Forest.",
    "Outputs: Precise Watering Schedule (Liters / Timing).",
    "Metrics: Accuracy, Precision, Recall.",
    "Contribution to Twin: Simulates soil dry-down to prevent over-watering and nutrient runoff."
])

# Slide 15: Risk Prediction Module
create_slide("Module 3: Agricultural Risk Prediction", [
    "Inputs: Meteorological Anomalies, Extreme Temperature Ranges.",
    "Algorithms: XGBoost Classifier.",
    "Outputs: Risk Probability Percentage (High/Medium/Low).",
    "Metrics: F1-Score, AUC-ROC.",
    "Contribution to Twin: Introduces virtual climatic shocks to test crop resilience."
])

# Slide 16: Methodology
create_slide("Methodology Overview", [
    "Phase 1: Data Collection (Synthetic generation & API integration).",
    "Phase 2: Data Preprocessing (Imputation, deduplication).",
    "Phase 3: Feature Engineering (Standard Scaling, One-Hot Encoding, Multicollinearity handling).",
    "Phase 4: Model Development (XGBoost/RF baseline with GridSearchCV tuning).",
    "Phase 5: Model Evaluation (Strict validation scoring).",
    "Phase 6: Digital Twin Development (Python logic routing).",
    "Phase 7: Dashboard Development (SPA integration)."
])

# Slide 17: Dashboard & Explainable AI
create_slide("Dashboard & Explainable AI (XAI)", [
    "Dashboard Features (Glassmorphism SPA):",
    "  - Visual gauges for Soil Status (NPK, Moisture) & Weather.",
    "  - Numerical outputs for Yield and Irrigation scheduling.",
    "  - Color-coded Risk Alerts and Historical Trend plotting.",
    "Explainable AI (SHAP):",
    "  - Unlocks the 'Black Box'.",
    "  - Feature Importance Breakdown.",
    "  - Decision Explanation (e.g., 'Yield reduced because pH contributed 60% negative impact')."
])

# Slide 18: Expected Results
create_slide("Expected Results", [
    "1. Improved Yield Prediction: Accurate, localized forecasting overriding generic regional estimates.",
    "2. Better Irrigation Planning: Prevention of water wastage and chemical runoff.",
    "3. Early Risk Detection: Actionable alerts prior to climatic shocks.",
    "4. Scenario Simulation: Farmers can safely test 'What-If' decisions virtually.",
    "5. Sustainable Agriculture: Long-term preservation of soil health aligned with SDGs."
])

# Slide 19: Project Status
create_slide("Project Status", [
    "COMPLETED:",
    "  - Literature Survey & Gap Analysis",
    "  - Objective Definition & Architecture Design",
    "  - Dataset Generation & Advanced EDA",
    "IN PROGRESS:",
    "  - Model Development (Hyperparameter tuning)",
    "  - Digital Twin Engine (API routing)",
    "  - Dashboard UI Implementation",
    "PLANNED:",
    "  - Real-Time Validation & Cloud Deployment"
])

# Slide 20: Future Scope
create_slide("Future Scope", [
    "IoT Deployment: Replacing synthetic data with live-streaming soil sensors.",
    "Satellite Imagery: Fusing ML models with remote sensing for macro-analysis.",
    "Mobile App: Progressive Web App (PWA) for field access.",
    "Reinforcement Learning: Self-optimizing AI agents that learn from seasonal feedback.",
    "Smart Farm Automation: Direct integration with automated irrigation valves."
])

# Slide 21: Conclusion
create_slide("Conclusion & Thank You", [
    "By transitioning from static predictions to interactive, transparent simulations, this AI-Driven Digital Twin Framework empowers smallholder farmers.",
    "It bridges the gap between global AI capabilities and the localized needs of Indian agriculture, fostering sustainability and resilience.",
    "",
    "Thank You.",
    "Questions & Answers."
])

prs.save("Stage_Review_With_Architecture.pptx")
print("Presentation created successfully as 'Stage_Review_With_Architecture.pptx'")
