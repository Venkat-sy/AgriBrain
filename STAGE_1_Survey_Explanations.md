# Survey Summaries (2023 - 2026)

This document provides a brief, bullet-point explanation for each of the 12 extracted surveys and research papers. To ensure comprehensive coverage, each year includes **two surveys focused on the Indian agricultural context** and **one survey with an international/global focus**.

## Year: 2023

### 1. Machine Learning Approaches for Kharif Crop Yield and Fertilizer Prediction (India)
* **Core Approach:** Employs Random Forest and Gradient Boosting algorithms to analyze specific seasonal crop needs.
* **Data Sources:** Uses Indian Ministry of Agriculture datasets focused specifically on Kharif crops.
* **Key Finding/Limitation:** Fails to account for sudden monsoon shifts that heavily impact Indian agriculture, creating a need to integrate live IMD (Indian Meteorological Department) data.

### 2. IoT-Based Soil Health Monitoring in Rural Maharashtra: A Case Study (India)
* **Core Approach:** Utilizes Support Vector Machines (SVM) running on edge devices for localized monitoring.
* **Data Sources:** Real-time IoT sensor data (N, P, K) gathered directly from farms in Maharashtra.
* **Key Finding/Limitation:** Plagued by high latency during monsoon network outages, prompting the need for offline Edge AI solutions tailored for rural connectivity.

### 3. Precision Agriculture: Deep Learning for Site-Specific Nutrient Management in the US Corn Belt (International)
* **Core Approach:** Uses Deep Convolutional Neural Networks (CNN) to make hyper-targeted nutrient recommendations.
* **Data Sources:** Relies on USDA hyperspectral satellite imagery combined with physical soil samples.
* **Key Finding/Limitation:** Heavily dependent on clear weather for satellite imaging, driving the global need for sensor fusion with ground-based IoT.

---

## Year: 2024

### 4. Advancements in Soil Quality Assessment: A Review of ML/AI Approaches for Indian Agriculture (India)
* **Core Approach:** Analyzes the effectiveness of traditional ML techniques (SVM, Decision Trees, KNN) for Indian soil.
* **Data Sources:** Evaluates various Indian agricultural datasets spanning both Kharif and Rabi crop seasons.
* **Key Finding/Limitation:** Concludes that these models act as "black-boxes," hindering trust among local farmers and necessitating Explainable AI (XAI) for transparency.

### 5. Low-Cost Fertilizer Recommendation Systems for Smallholder Indian Farms (India)
* **Core Approach:** Introduces TinyML and lightweight decision trees capable of running on affordable, low-power microcontrollers.
* **Data Sources:** Processes data locally from low-cost soil sensors tested in Punjab and Haryana.
* **Key Finding/Limitation:** Faces a trade-off with reduced model accuracy compared to large-scale cloud models, pushing future research toward localized federated learning.

### 6. Global Blockchain and AI Integration for Transparent Fertilizer Supply Chains (International)
* **Core Approach:** Combines Blockchain Smart Contracts with Support Vector Regression (SVR).
* **Data Sources:** Utilizes European and global supply chain ledger records.
* **Key Finding/Limitation:** While highly transparent, the massive implementation costs make it currently unfeasible for developing nations without significant modification.

---

## Year: 2025

### 7. Fertilizer Recommendation for Agriculture using Machine Learning (India)
* **Core Approach:** Leverages robust ensemble models, specifically Random Forest and XGBoost.
* **Data Sources:** Built primarily around the Indian Soil Health Card (SHC) dataset encompassing N, P, K, and pH levels.
* **Key Finding/Limitation:** Focuses mostly on broad macronutrients and struggles with localized micro-climate variations across different Indian states.

### 8. Generative AI based Fertilizer and Pesticide Recommendation System (India)
* **Core Approach:** Uses Generative AI and Natural Language Processing (NLP) to provide conversational farming advice.
* **Data Sources:** Trained on multilingual regional crop datasets in India (supporting Hindi, Tamil, Telugu, etc.).
* **Key Finding/Limitation:** Prone to AI hallucinations as it relies on secondary advisory data rather than live sensors; needs coupling with in-situ IoT sensors for ground truth.

### 9. Explainable AI in Global Soil Property Prediction Models (International)
* **Core Approach:** Merges Deep Learning with globally recognized XAI frameworks (like SHAP and LIME).
* **Data Sources:** Uses the Global Soil Data Facility and large-scale Australian IoT sensor datasets.
* **Key Finding/Limitation:** The heavy computational requirement for running these advanced XAI frameworks limits their deployability in resource-constrained edge environments.

---

## Year: 2026

### 10. Digital Twins for Hyper-Local Soil Management in the Gangetic Plains (India)
* **Core Approach:** Pairs continuous Digital Twin simulations with Reinforcement Learning for dynamic crop advisories.
* **Data Sources:** Processes multi-temporal drone imagery alongside live IoT streams specifically from Uttar Pradesh and Bihar.
* **Key Finding/Limitation:** Demands extreme computational cost and robust 5G connectivity, requiring adaptation for low-bandwidth LoRaWAN networks in Indian villages.

### 11. Predictive Modeling of Nutrient Deficiencies Using Multi-Modal AI for Indian Horticulture (India)
* **Core Approach:** Utilizes Vision Transformers (ViT) and multi-modal AI to detect deficiencies visually and chemically.
* **Data Sources:** Crop leaf imaging and soil data gathered from South Indian horticulture farms.
* **Key Finding/Limitation:** High cost of image acquisition hardware for farmers, pointing towards a need for lightweight, smartphone-based ViT models.

### 12. Magnetotactic Bacteria Optimized K-Nearest Neighbour-Tuned Tree Algorithm in Digital Twins (International)
* **Core Approach:** Proposes an advanced Hybrid AI Framework paired with large-scale Digital Twin technology.
* **Data Sources:** Fuses multi-modal IoT data streams with European Space Agency (ESA) Satellite Imagery.
* **Key Finding/Limitation:** Features extremely high setup costs and an absolute reliance on continuous cloud connectivity, challenging its global scalability.
