# Project Synopsis

**Title:** AI-Driven Digital Twin Framework for Sustainable Agriculture: A What-If Simulation System for Crop Yield, Irrigation, and Risk Assessment

## Problem Statement
Agriculture is increasingly affected by climate variability, soil degradation, water scarcity, and inefficient resource utilization. Existing intelligent farming systems primarily focus on predicting crop yield or recommending irrigation schedules using historical datasets. However, they lack the capability to simulate future farming scenarios and estimate the impact of changing environmental conditions before implementation. 

Farmers and agricultural planners require an intelligent decision-support system capable of evaluating multiple "what-if" situations, such as reduced rainfall, increased fertilizer application, or changes in irrigation practices, before making field-level decisions. Therefore, there is a need for an AI-powered Digital Twin framework that combines crop yield prediction, irrigation demand estimation, agricultural risk assessment, and real-time scenario simulation to support sustainable and data-driven farming practices.

## Objectives
- To develop an AI-based crop yield prediction model using environmental and soil parameters.
- To design an intelligent irrigation prediction model for efficient water management.
- To develop a crop risk prediction module that estimates agricultural risks under varying climatic conditions.
- To implement a Digital Twin simulation engine capable of performing "what-if" scenario analysis.
- To build an interactive dashboard that provides decision support using explainable AI techniques for sustainable agriculture.

## Methodology
The proposed work follows a systematic AI-driven Digital Twin framework for precision agriculture.

Initially, agricultural datasets containing soil nutrients (Nitrogen, Phosphorus, Potassium), pH, rainfall, temperature, humidity, soil moisture, crop type, and crop yield are collected from publicly available sources such as Kaggle, UCI Repository, and government agriculture portals.

The collected data undergo preprocessing including missing value treatment, outlier removal, normalization, categorical encoding, and exploratory data analysis. The cleaned dataset is then used to develop three independent AI prediction modules:
1. **Crop Yield Prediction** using Decision Tree, Random Forest, and XGBoost algorithms.
2. **Irrigation Prediction** based on weather and soil parameters.
3. **Agricultural Risk Prediction** for estimating crop failure risks.

The performance of the models is evaluated using appropriate regression and classification metrics such as MAE, RMSE, R² Score, Accuracy, Precision, Recall, and F1-score.

The novelty of the proposed system lies in the Digital Twin Simulation Engine, where users can modify environmental variables (rainfall, fertilizer levels, irrigation amount, temperature, etc.) to simulate multiple future agricultural scenarios. The framework predicts the corresponding crop yield, irrigation requirements, and agricultural risks without performing real-world experiments.

Finally, an interactive dashboard developed using Streamlit visualizes the current farm status, predicted outputs, scenario comparisons, feature importance, and explainable AI insights using SHAP values, thereby enabling informed decision-making for sustainable farming.

<br><br><br>

---

**Project Guide**  
Mr. Krishna Prasad D S  
Assistant Professor Gd-II  

**Project Coordinator**  
Dr. Radhakrishna  
Professor & Head
