import collections
import collections.abc
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor

# Fix for pptx collections issue
collections.Sequence = collections.abc.Sequence

def add_notes(slide, notes_text):
    notes_slide = slide.notes_slide
    text_frame = notes_slide.notes_text_frame
    text_frame.text = notes_text

def apply_styling(tf, font_size=Pt(20), color=RGBColor(50, 50, 50), bold=False):
    for p in tf.paragraphs:
        for run in p.runs:
            run.font.size = font_size
            run.font.color.rgb = color
            run.font.bold = bold

prs = Presentation()

# Define Colors
GREEN = RGBColor(34, 139, 34)
BLUE = RGBColor(0, 102, 204)
WHITE = RGBColor(255, 255, 255)
DARK_GRAY = RGBColor(50, 50, 50)

# Slide 1: Title Slide
slide_layout = prs.slide_layouts[0] # Title slide
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "AI-Driven Digital Twin Framework for Sustainable Agriculture"
subtitle.text = "A What-If Simulation System for Crop Yield, Irrigation, and Risk Assessment\n\nPresented By: K. Venkatesh Hebbar\nGuide: Mr. Krishna Prasad D S (Assistant Professor Gd-II)\nProject Coordinator: Dr. Radhakrishna (Professor & Head)\n\nDepartment of Computer and Communication Engineering\nNMAM Institute of Technology, Nitte"

# Styling title
for p in title.text_frame.paragraphs:
    p.font.color.rgb = GREEN
    p.font.bold = True
    p.font.size = Pt(36)

add_notes(slide, "Introduce the project as an AI-powered decision support system that helps farmers predict crop yield, irrigation needs, agricultural risks, and evaluate future farming scenarios using Digital Twin technology.")

# Slide 2: Introduction and Problem Statement
slide_layout = prs.slide_layouts[1] # Title and Content
slide = prs.slides.add_slide(slide_layout)
title = slide.shapes.title
content = slide.placeholders[1]
title.text = "Introduction & Problem Statement"

content.text = "Agriculture Challenges:\n"
content.text += "• Climate variability & Water scarcity\n"
content.text += "• Soil degradation & Increasing production demands\n\n"
content.text += "Current intelligent farming systems:\n"
content.text += "• Predict crop yield & Recommend irrigation schedules\n"
content.text += "• Limitations: Cannot simulate future scenarios, lack integrated decision support\n\n"
content.text += "Problem Statement (Farmers need answers to):\n"
content.text += "• 'What will happen if rainfall decreases?'\n"
content.text += "• 'What if irrigation is reduced?'\n"
content.text += "• 'What if fertilizer application increases?'"

title.text_frame.paragraphs[0].font.color.rgb = BLUE
add_notes(slide, "Explain how current systems only provide predictions while farmers require predictive simulation before taking action.")

# Insert an image for slide 2 (ai_agri_concept)
img_path = r"C:\Users\USER\.gemini\antigravity-ide\brain\789a9f68-c59a-42e7-8691-411dfb7de6e5\ai_agri_concept_1787821726812.png"
slide.shapes.add_picture(img_path, Inches(6.5), Inches(2), Inches(3), Inches(3))

# Slide 3: Research Gap and Motivation
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Research Gap & Motivation"
title.text_frame.paragraphs[0].font.color.rgb = BLUE

content = slide.placeholders[1]
content.text = "Existing Research Focus:\n"
content.text += "• Crop Yield Prediction, Irrigation Recommendation, Weather, Disease\n\n"
content.text += "Research Gap:\n"
content.text += "Most existing systems work independently (Single objective).\n"
content.text += "Missing: Integrated framework, Digital Twin, Multi-scenario simulation.\n\n"
content.text += "Proposed System vs Existing Systems:\n"
content.text += "• Prediction + Simulation vs Prediction only\n"
content.text += "• Multi-objective framework vs Single-purpose models\n"
content.text += "• Digital Twin enabled vs No simulation\n\n"
content.text += "Motivation:\n"
content.text += "Develop a sustainable agriculture framework to test decisions virtually."

add_notes(slide, "Emphasize that the Digital Twin simulation engine is the key novelty and research contribution.")

# Slide 4: Objectives
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Project Objectives"
title.text_frame.paragraphs[0].font.color.rgb = GREEN

content = slide.placeholders[1]
content.text = "1. Develop an AI-based Crop Yield Prediction Model.\n\n"
content.text += "2. Develop an Intelligent Irrigation Prediction Model.\n\n"
content.text += "3. Develop an Agricultural Risk Prediction Module.\n\n"
content.text += "4. Implement a Digital Twin Simulation Engine.\n\n"
content.text += "5. Develop an Explainable AI Dashboard for decision support."

add_notes(slide, "Explain how each objective contributes toward sustainable and intelligent farming.")

# Slide 5: Crop Yield Prediction Module
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Objective 1 – Crop Yield Prediction"
title.text_frame.paragraphs[0].font.color.rgb = BLUE

content = slide.placeholders[1]
content.text = "Purpose:\n"
content.text += "Predict crop yield using environmental and soil parameters.\n\n"
content.text += "Input Parameters:\n"
content.text += "• Nitrogen (N), Phosphorus (P), Potassium (K), pH\n"
content.text += "• Rainfall, Temperature, Humidity\n\n"
content.text += "Algorithms:\n"
content.text += "• Decision Tree, Random Forest, XGBoost\n\n"
content.text += "Evaluation Metrics:\n"
content.text += "• MAE, RMSE, R² Score"

add_notes(slide, "Describe how machine learning algorithms learn relationships between environmental factors and crop productivity.")
# Add farming image
img_path2 = r"C:\Users\USER\.gemini\antigravity-ide\brain\789a9f68-c59a-42e7-8691-411dfb7de6e5\smart_farming_1787821697959.png"
slide.shapes.add_picture(img_path2, Inches(6), Inches(2.5), Inches(3.5), Inches(2.5))

# Slide 6: Irrigation Prediction and Risk Assessment
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Objectives 2 & 3 – Irrigation & Risk Assessment"
title.text_frame.paragraphs[0].font.color.rgb = GREEN

content = slide.placeholders[1]
content.text = "Irrigation Prediction:\n"
content.text += "• Inputs: Soil Moisture, Rainfall, Temp, Humidity, Crop Type\n"
content.text += "• Outputs: Irrigation Demand, Water Requirement\n"
content.text += "• Benefits: Water conservation, Efficient scheduling\n\n"
content.text += "Agricultural Risk Prediction:\n"
content.text += "• Risks: Drought, Crop Failure, Water Stress, Climate Variability\n"
content.text += "• Outputs: Low, Medium, High Risk\n"
content.text += "• Metrics: Accuracy, Precision, Recall, F1 Score"

add_notes(slide, "Explain how irrigation optimization and risk prediction improve sustainability and reduce farming losses.")

# Slide 7: Methodology
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Methodology"
title.text_frame.paragraphs[0].font.color.rgb = BLUE

content = slide.placeholders[1]
content.text = "Phase 1: Data Collection (Kaggle, UCI, Govt Portals)\n"
content.text += "Phase 2: Data Preprocessing\n"
content.text += "   • Missing Values, Outliers, Normalization, Encoding, EDA\n"
content.text += "Phase 3: Model Development\n"
content.text += "   • Yield, Irrigation, and Risk Models\n"
content.text += "Phase 4: Performance Evaluation\n"
content.text += "Phase 5: Digital Twin Development\n"
content.text += "Phase 6: Dashboard Development"

add_notes(slide, "Walk through the complete workflow from data collection to deployment.")

# Slide 8: Proposed Architecture & Digital Twin
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Architecture & Digital Twin Simulation"
title.text_frame.paragraphs[0].font.color.rgb = GREEN

content = slide.placeholders[1]
content.text = "Digital Twin What-If Simulation Examples:\n"
content.text += "• Scenario 1: Rainfall decreases by 20%\n"
content.text += "• Scenario 2: Fertilizer increases by 15%\n"
content.text += "• Scenario 3: Temperature rises by 3°C\n"
content.text += "• Scenario 4: Irrigation reduced by 10%\n\n"
content.text += "Outputs:\n"
content.text += "• Yield Changes, Water Requirement, Risk Level"

add_notes(slide, "Highlight this slide as the core innovation of the project.")

# Add arch image
img_path3 = r"C:\Users\USER\.gemini\antigravity-ide\brain\789a9f68-c59a-42e7-8691-411dfb7de6e5\digital_twin_arch_1787821712189.png"
slide.shapes.add_picture(img_path3, Inches(5), Inches(2), Inches(4.5), Inches(3.5))

# Slide 9: Expected Results, Benefits and Impact
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Expected Results & Benefits"
title.text_frame.paragraphs[0].font.color.rgb = BLUE

content = slide.placeholders[1]
content.text = "Expected Performance:\n"
content.text += "• Yield Prediction R² Score > 90% | Risk Accuracy > 90%\n\n"
content.text += "Before Project vs After Project:\n"
content.text += "• Manual decisions → Data-driven farming\n"
content.text += "• High uncertainty → Smart irrigation & Early risk detection\n"
content.text += "• Resource wastage → Sustainable resource utilization\n\n"
content.text += "Impact:\n"
content.text += "• Supports precision agriculture\n"
content.text += "• Reduces water wastage\n"
content.text += "• Enhances food security & sustainable farming"

add_notes(slide, "Discuss the practical benefits to farmers and agricultural planners.")

# Slide 10: Conclusion and Future Scope
slide = prs.slides.add_slide(prs.slide_layouts[1])
title = slide.shapes.title
title.text = "Conclusion & Future Scope"
title.text_frame.paragraphs[0].font.color.rgb = GREEN

content = slide.placeholders[1]
content.text = "Conclusion:\n"
content.text += "• Integrated AI-powered Digital Twin framework.\n"
content.text += "• Simulates future scenarios for smart decision-making.\n\n"
content.text += "Future Scope:\n"
content.text += "• IoT Sensor & Satellite Image Integration\n"
content.text += "• Weather API & Mobile App Development\n"
content.text += "• Smart Farm Automation via Reinforcement Learning\n\n"
content.text += "Final Message:\n"
content.text += "\"Transforming Traditional Farming into Intelligent Sustainable Agriculture Through AI and Digital Twins\""

add_notes(slide, "Conclude by emphasizing innovation, sustainability, and real-world impact.")

prs.save("AI_Agriculture_Presentation.pptx")
print("Presentation generated successfully!")
