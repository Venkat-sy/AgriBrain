# PART A — LITERATURE SURVEY ANALYSIS

## Step 1: Categorize Papers According to Project Objectives

**Objective 1: Crop Yield Prediction**
* Interpretable deep learning models for independent fertilizer and crop recommendation (2023)
* On-device AI for climate-resilient farming with intelligent crop yield prediction using lightweight models (2023)
* Non-destructive yield estimation of onion and garlic using UAV-based hyperspectral imaging and hybrid machine learning models (2023)
* An explainable AI-based hybrid machine learning model for interpretability and enhanced crop yield prediction (2024)
* Enhancing precision agriculture through cloud based transformative crop recommendation model (2024)
* Maize yield prediction using machine learning: a systematic literature review (2024)
* Soil test crop response based fertilizer calibration and soil nutrient forecasting for aerobic rice on Alfisols (2025)
* Towards enhancing the performance of crop prediction system for precision agriculture using feature correlation (2026)

**Objective 2: Irrigation Prediction**
* Not Specified in Survey.

**Objective 3: Agricultural Risk Prediction**
* On-device AI for climate-resilient farming with intelligent crop yield prediction using lightweight models (2023)
* Regional machine learning-based estimation of methane emissions from rice cultivation (2025)

**Objective 4: Digital Twin Simulation**
* Not Specified in Survey. *(Note: "Digital Twin" is mentioned as a proposed system concept in the research gap, but no existing papers in the survey explicitly cover it.)*

**Objective 5: Explainable AI Dashboard**
* Interpretable deep learning models for independent fertilizer and crop recommendation (2023)
* An explainable AI-based hybrid machine learning model for interpretability and enhanced crop yield prediction (2024)
*(Note: Papers cover Explainable AI, but a "Dashboard" is Not Specified in Survey as an existing implementation.)*

---

## Step 2: Select Representative Papers by Year

| Year | Paper | Objective | Reason for Selection |
| :--- | :--- | :--- | :--- |
| 2023 | Interpretable deep learning models for independent fertilizer and crop recommendation | Crop Yield Prediction, Explainable AI | Highlights the foundational use of Deep Learning and SHAP for transparent prediction using soil datasets. |
| 2024 | An explainable AI-based hybrid machine learning model for interpretability and enhanced crop yield prediction | Crop Yield Prediction, Explainable AI | Demonstrates the progression to hybrid ensemble models combined with XAI, identifying unstructured weather data as a gap. |
| 2025 | Agentic AI-driven autonomous decision support system for smart agriculture | Agricultural Automation / General | Showcases cutting-edge autonomous decision trees via Agentic AI and continuous live IoT data streams. |
| 2026 | An evaluation of machine learning for soil analysis in internet of things-enabled smart farming | IoT Integration / General | Provides critical insights into real-world IoT deployment challenges like sensor drift in end-to-end ML pipelines. |

---

## Step 3: Generate Objective-Wise Comparative Tables

### Crop Yield Prediction

| Year | Author/Paper | Dataset Source | Features | Algorithm | Results | Advantages | Limitations | Research Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2023 | Interpretable deep learning models for independent fertilizer and crop recommendation | Indian soil and weather datasets | N, P, K, pH, weather metrics | Deep Learning, SHAP | High accuracy | Transparent decision-making | Requires large amounts of curated soil data | Needs real-time edge processing |
| 2024 | An explainable AI-based hybrid machine learning model for interpretability and enhanced crop yield prediction | Regional agricultural boards | Indian soil and crop yield statistics | Hybrid ML (Random Forest, XGBoost), XAI | Enhanced interpretability | High interpretability | Struggles with unstructured meteorological data | Needs integration of real-time weather APIs |
| 2026 | Towards enhancing the performance of crop prediction system for precision agriculture using feature correlation | Comprehensive Indian agro-climatic datasets | Agro-climatic variables, soil data | Feature Correlation Square-based KNN | Improved predictions | Isolates impactful variables | Computationally heavy for large feature spaces | Needs quantum-inspired optimization algorithms |

### Irrigation Prediction

| Year | Author/Paper | Dataset Source | Inputs | Algorithm | Findings | Advantages | Limitations | Research Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| N/A | Not Specified in Survey | Not Specified | Not Specified | Not Specified | Not Specified | Not Specified | Not Specified | Not Specified |

### Agricultural Risk Prediction

| Year | Author/Paper | Dataset Source | Risk Type | Algorithm | Results | Advantages | Limitations | Research Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2023 | On-device AI for climate-resilient farming... | Localized Indian sensor data | Climate Resilience | Lightweight ML | Real-time inference | Eliminates constant cloud connectivity | Limited computational capacity on-device | Expanding to drone integration |
| 2025 | Regional machine learning-based estimation of methane emissions... | South Korean regional emission datasets | Greenhouse Emissions (Methane) | Spatial ML | Emission tracking | Tracks regional emissions effectively | Not calibrated for tropical climates | Needs global multi-climate tracking |

### Digital Twin Simulation

| Year | Author/Paper | Technology Used | Dataset | Components | Advantages | Limitations | Research Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| N/A | Not Specified in Survey | Not Specified | Not Specified | Not Specified | Not Specified | Not Specified | Not Specified |

### Explainable AI Dashboard

| Year | Author/Paper | XAI Technique | Dataset | AI Model | Benefits | Limitations | Research Gap |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 2023 | Interpretable deep learning models for independent fertilizer and crop recommendation | SHAP | Soil (N, P, K, pH), weather | Deep Learning | Transparent decision-making | Requires large curated data | Dashboard Not Specified in Survey |
| 2024 | An explainable AI-based hybrid machine learning model... | Explainable AI (General) | Indian soil and yield statistics | Hybrid ML (RF, XGBoost) | Details influence of specific features | Struggles with sudden weather changes | Dashboard Not Specified in Survey |

---

## Step 4: Dataset Extraction

| Paper | Dataset Name | Dataset Source | Features | Country/Region | Dataset Type | Public/Private |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Interpretable deep learning models... (2023) | Not Specified in Survey | Soil and weather datasets | N, P, K, pH, weather metrics | India | Not Specified in Survey | Not Specified in Survey |
| On-device AI for climate-resilient farming... (2023) | Not Specified in Survey | Localized Indian sensor data | Micro-climate variations | India | Sensor logs | Not Specified in Survey |
| Non-destructive yield estimation of onion and garlic... (2023) | Not Specified in Survey | Global agricultural hyperspectral image datasets | Hyperspectral images | Global | Imagery | Not Specified in Survey |
| An explainable AI-based hybrid machine learning model... (2024) | Not Specified in Survey | Regional agricultural boards | Indian soil profiling data, crop yield statistics | India | Statistics / Profiling | Not Specified in Survey |
| Enhancing precision agriculture through cloud based... (2024) | Soil Health Card datasets | Regional Soil Health Card data | Soil health parameters | India | Digitized Cards | Not Specified in Survey |
| Maize yield prediction using machine learning... (2024) | Not Specified in Survey | Global historical datasets | Historical maize yields | Global | Historical | Not Specified in Survey |
| Soil test crop response based fertilizer calibration... (2025) | Alfisols datasets | Aerobic rice fields | Alfisol soil metrics | India (Southern) | Agronomic | Not Specified in Survey |
| Agentic AI-driven autonomous decision support system... (2025) | Not Specified in Survey | Live IoT sensor arrays in Indian test farms | Continuous data streams | India | IoT Sensor | Not Specified in Survey |
| Regional machine learning-based estimation of methane... (2025) | Not Specified in Survey | Regional emission datasets | Methane emissions | South Korea | Spatial / Emission | Not Specified in Survey |
| An evaluation of machine learning for soil analysis... (2026) | Not Specified in Survey | Smart farms | Millions of time-series NPK sensor logs | India | Time-series Sensor | Not Specified in Survey |
| Towards enhancing the performance of crop prediction... (2026) | Not Specified in Survey | Comprehensive agro-climatic datasets | Soil variables, agro-climatic data | India | Agro-climatic | Not Specified in Survey |
| Enhancing precision nitrogen management in corn... (2026) | Not Specified in Survey | Global satellite imagery, ground-truth sampling | Soil properties, remote sensing | Global | Multi-modal | Not Specified in Survey |

---

## Step 5: Research Gap Analysis

| Objective | Existing Work | Limitation | Gap Identified | Proposed Solution |
| :--- | :--- | :--- | :--- | :--- |
| Crop Yield Prediction | Traditional predictive ML & Deep Learning | Black-box nature, static datasets, lacks adaptability to climatic shocks | "Predict Only" models fail to simulate forward-looking outcomes | "Predict + Simulate Future Scenarios" using XAI |
| Irrigation Prediction | Not Specified in Survey | Not Specified in Survey | Not Specified in Survey | Digital Twin simulation for what-if scenarios (derived from proposal) |
| Risk Assessment | Methane tracking, localized on-device AI | Highly localized, struggles with unstructured meteorological anomalies | Lack of integrated risk simulation for weather/monsoon shocks | Simulating climatic shocks via Digital Twins |
| Digital Twin Simulation | IoT-enabled smart farming, Agentic AI | High setup complexity, hardware cost, sensor drift | Absence of localized Digital Twin platforms for smallholders | Localized Digital Twin concepts bridging global AI and local needs |
| Explainable AI Dashboard | Hybrid ML with SHAP and XAI | Output a single dose without continuous interactive interfaces | Lack of user-friendly interactive explanation tools | System providing transparent reasoning in regional contexts |

---

## Step 6: Research Gap Matrix

| Feature | Existing Papers | Proposed System |
| :--- | :--- | :--- |
| Crop Yield Prediction | ✓ | ✓ |
| Irrigation Prediction | ✗ | ✓ |
| Risk Assessment | ✓ | ✓ |
| Explainable AI | ✓ | ✓ |
| IoT Integration | ✓ | ✓ |
| Dashboard | ✗ | ✓ |
| Digital Twin | ✗ | ✓ |
| What-If Analysis | ✗ | ✓ |
| Scenario Simulation | ✗ | ✓ |
