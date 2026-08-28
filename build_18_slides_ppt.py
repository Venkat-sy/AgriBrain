from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
import collections
import collections.abc
collections.Sequence = collections.abc.Sequence

prs = Presentation()

GREEN = RGBColor(34, 139, 34)
BLUE = RGBColor(0, 102, 204)

def add_slide(title_text, content_text):
    slide = prs.slides.add_slide(prs.slide_layouts[1])
    title = slide.shapes.title
    title.text = title_text
    title.text_frame.paragraphs[0].font.color.rgb = BLUE
    content = slide.placeholders[1]
    content.text = content_text
    return slide

# Slide 1
slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]
title.text = "AI-Driven Digital Twin Framework for Sustainable Agriculture"
subtitle.text = "A Digital Agriculture-Based What-If Simulation System for Crop Yield, Irrigation, and Risk Assessment\n\nPresented By: K. Venkatesh Hebbar\nGuide: Mr. Krishna Prasad D S\nProject Coordinator: Dr. Radhakrishna\nDepartment of Computer and Communication Engineering\nNMAM Institute of Technology, Nitte"
title.text_frame.paragraphs[0].font.color.rgb = GREEN

# Slide 2
add_slide("Introduction to Digital Agriculture", 
    "• Context: The agricultural sector is the backbone of the Indian economy but faces immense challenges due to climate unpredictability and soil degradation.\n"
    "• Transition: Moving from traditional static fertilizer recommendation to dynamic data-driven agriculture.\n"
    "• Integration: Combining Machine Learning (ML), IoT sensors, and Artificial Intelligence (AI) to optimize resource allocation.\n"
    "• Goal: Moving beyond 'Predict Only' models to 'Predict + Simulate Future Scenarios'.")

# Slide 3
add_slide("Digital Agriculture & Sustainable Development Goals",
    "• Sustainable Development Goals (SDGs): Not Specified in Survey.\n\n"
    "Note: The uploaded survey does not explicitly map its findings to specific SDGs, but the overarching theme aligns with sustainable, climate-resilient farming.")

# Slide 4
add_slide("Literature Survey (Crop Yield & Irrigation)",
    "Group Focus: Crop Yield Prediction & Irrigation Prediction\n\n"
    "1. Hybrid ML (RF, XGBoost) [2024]\n"
    "   - Key Finding: Enhanced crop yield prediction via ensemble\n"
    "   - Limitation: Struggles with unstructured meteorological data\n\n"
    "2. Meta-Analysis & Review [2024]\n"
    "   - Key Finding: Evaluates efficacy of various ML for Maize\n"
    "   - Limitation: Lack of standardization in ML metrics\n\n"
    "3. Feature Correlation KNN [2026]\n"
    "   - Key Finding: Isolates impactful soil variables for prediction\n"
    "   - Limitation: Computationally heavy for large feature spaces\n\n"
    "• Irrigation Prediction: Not Specified in Survey.")

# Slide 5
add_slide("Literature Survey (Risk Prediction & Explainable AI)",
    "Group Focus: Risk Prediction & Explainable AI Papers\n\n"
    "1. Deep Learning, SHAP [2023]\n"
    "   - Key Finding: Highly accurate, transparent crop/fertilizer prep\n"
    "   - Limitation: Requires large amounts of curated soil data\n\n"
    "2. Lightweight ML on Edge [2023]\n"
    "   - Key Finding: Eliminates constant cloud connectivity\n"
    "   - Limitation: Limited computational capacity on-device\n\n"
    "3. Spatial ML [2025]\n"
    "   - Key Finding: Effectively maps regional methane emissions\n"
    "   - Limitation: Not calibrated for tropical climates")

# Slide 6
add_slide("Literature Survey (Digital Agriculture & Digital Twin)",
    "Group Focus: Digital Agriculture & Autonomous Systems\n\n"
    "1. Agentic AI [2025]\n"
    "   - Key Finding: Continuous advisory via autonomous agents\n"
    "   - Limitation: High setup complexity and maintenance\n\n"
    "2. IoT-ML Pipelines [2026]\n"
    "   - Key Finding: Critical evaluation of end-to-end performance\n"
    "   - Limitation: Sensor drift causes long-term accuracy decay\n\n"
    "3. Mechanistic + Remote Sensing [2026]\n"
    "   - Key Finding: Fuses satellite imagery with ground truth\n"
    "   - Limitation: Complex integration pipeline introduces latency\n\n"
    "• Digital Twin Specifics: Not Specified in Survey.")

# Slide 7
add_slide("Research Gap & Problem Statement",
    "Problem Statement:\n"
    "Current systems are strictly 'Predict Only' black boxes that rely on static datasets and fail to provide forward-looking simulations adaptable to local climatic shocks.\n\n"
    "Research Gap Matrix (Existing vs Proposed):\n"
    "• Crop Yield Prediction: Existing ✓ | Proposed ✓\n"
    "• Irrigation Prediction: Existing ✗ | Proposed ✓\n"
    "• Risk Assessment: Existing ✓ (Partial) | Proposed ✓\n"
    "• Explainable AI: Existing ✓ | Proposed ✓\n"
    "• IoT Integration: Existing ✓ | Proposed ✓\n"
    "• Dashboard / Digital Twin: Existing ✗ | Proposed ✓\n"
    "• What-If Analysis / Simulation: Existing ✗ | Proposed ✓")

# Slide 8
add_slide("Objectives",
    "1. Crop Yield Prediction:\n   Develop accurate, transparent models for yield and fertilizer recommendations.\n\n"
    "2. Irrigation Prediction:\n   Implement predictive models for optimal water usage.\n\n"
    "3. Agricultural Risk Prediction:\n   Forecast risks such as climate shock impacts and emission anomalies.\n\n"
    "4. Digital Twin Simulation:\n   Create a localized virtual representation of a farm for what-if scenario testing.\n\n"
    "5. Explainable AI Dashboard:\n   Build an intuitive interface providing transparent reasoning for AI decisions.")

# Slide 9
add_slide("Dataset Structure & Features",
    "Flowchart:\n"
    "Input Data → Preprocessing → Feature Engineering → Model Training → Predictions\n\n"
    "Extracted Datasets:\n"
    "• Soil & weather datasets (India) - N,P,K,pH, weather metrics\n"
    "• Localized Indian sensor data - Micro-climate variations\n"
    "• Regional Soil Health Card data (India) - Soil health parameters\n"
    "• Live IoT sensor arrays (India) - Continuous data streams\n"
    "• Regional emission datasets (South Korea) - Methane emissions")

# Slide 10
add_slide("Crop Yield Prediction Module",
    "• Algorithms:\n"
    "  - Deep Learning\n"
    "  - Hybrid ML (Random Forest, XGBoost)\n"
    "  - K-Nearest Neighbor (KNN)\n\n"
    "• Inputs:\n"
    "  - N, P, K, pH\n"
    "  - Weather metrics, micro-climate variations, satellite imagery\n\n"
    "• Outputs:\n"
    "  - Crop yield estimations, specific fertilizer dose recommendations\n\n"
    "• Metrics:\n"
    "  - Not Specified in Survey (Standardization of ML metrics identified as a gap).")

# Slide 11
add_slide("Irrigation Prediction + Risk Prediction",
    "Irrigation Prediction:\n"
    "• Details: Not Specified in Survey.\n\n"
    "Risk Prediction:\n"
    "• Methods:\n"
    "  - Spatial ML\n"
    "  - Lightweight ML on Edge Devices\n"
    "  - Geospatial Emission Modeling\n\n"
    "• Risks Tracked:\n"
    "  - Methane greenhouse emissions\n"
    "  - Unstructured meteorological anomalies (delayed monsoons)")

# Slide 12
add_slide("Proposed System Architecture",
    "Flow:\n"
    "Agricultural Field → Sensors → Data Collection → Cloud → Analytics → AI Models → Digital Twin → Dashboard → Decision Support\n\n"
    "• Data Collection: IoT sensors streaming micro-climate and NPK data.\n\n"
    "• Cloud & Analytics: Cloud-based ML frameworks processing data.\n\n"
    "• Decision Support: Translating numerical soil data into actionable, continuous advice.")

# Slide 13
add_slide("Digital Twin Simulation Engine",
    "Concept: Physical Farm ↔ Digital Twin\n\n"
    "• Yield Prediction:\n  Integrating STCR equations and ML forecasting.\n\n"
    "• Irrigation Prediction:\n  Simulating future water needs based on live variables.\n\n"
    "• Risk Prediction:\n  Modeling the effects of hardware degradation (sensor drift) and environmental anomalies.\n\n"
    "• What-If Scenarios:\n  E.g., 'How will a delayed monsoon affect the current fertilizer dosage?'")

# Slide 14
add_slide("Methodology",
    "Workflow Pipeline:\n\n"
    "1. Data Collection: Sourcing regional soil profiles and live IoT sensor logs.\n"
    "2. Preprocessing: Handling unstructured meteorological data and standardizing metrics.\n"
    "3. Model Development: Training Hybrid ML and Deep Learning algorithms.\n"
    "4. Evaluation: Assessing against baseline static models.\n"
    "5. Digital Twin: Integrating the models into a continuous, simulated feedback loop.\n"
    "6. Dashboard: Deploying the XAI interface for the end-user.")

# Slide 15
add_slide("Dashboard & Explainable AI",
    "• XAI Techniques:\n  - SHAP (SHapley Additive exPlanations).\n\n"
    "• Feature Importance:\n  - Detailing exactly how much influence nitrogen, pH, or weather had on the recommendation.\n\n"
    "• Decision Explanation:\n  - Bridging the gap between advanced global AI and local smallholder trust by providing transparent reasoning.\n\n"
    "[INSERT DASHBOARD SCREENSHOT HERE]")

# Slide 16
add_slide("Expected Results & Project Status",
    "Completed:\n"
    "• Literature Survey\n"
    "• Research Gap Analysis\n"
    "• Objectives\n"
    "• Architecture Design\n\n"
    "In Progress:\n"
    "• Model Development\n"
    "• Digital Twin Development\n"
    "• Dashboard Development")

# Slide 17
add_slide("Future Scope",
    "• IoT Deployment: Auto-calibrating ML models for sensor degradation.\n\n"
    "• Satellite Imagery: Developing fully automated drone-to-tractor delivery.\n\n"
    "• Weather API: Integrating real-time weather forecasting APIs.\n\n"
    "• Fog/Edge Computing: Shifting to fog computing architectures for rural areas.\n\n"
    "• Optimization: Quantum-inspired optimization algorithms.\n\n"
    "• Mobile App / Smart Farm Automation: Extending the Agentic AI to zero-configuration autonomous agents.")

# Slide 18
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Conclusion & Thank You"
title.text_frame.paragraphs[0].font.color.rgb = GREEN
content = slide.placeholders[1]
content.text = "\n\n\nTransforming Traditional Farming into Intelligent Sustainable Agriculture through AI-Powered Digital Twins.\n\n\nThank You!"
from pptx.enum.text import PP_ALIGN
for p in content.text_frame.paragraphs:
    p.alignment = PP_ALIGN.CENTER

prs.save("Final_Project_Presentation.pptx")
print("Presentation generated successfully!")
