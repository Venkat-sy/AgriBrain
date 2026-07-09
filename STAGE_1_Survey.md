# STAGE 1 (Weeks 1-4) - Literature Survey & Research Gap

## Deliverables

### 1. Literature Table

#### Year: 2023
| Paper Title | Methodology & Algorithm / Technique | Dataset | Limitation | Future Scope | Source / Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Interpretable deep learning models for independent fertilizer and crop recommendation (2023)** | Deep Learning, SHAP (Utilizes neural networks and SHAP values for transparent crop prediction) | N, P, K, pH and weather datasets | Requires large amounts of curated soil data. | Incorporating real-time edge processing for remote farms. | [*Scientific Reports (Nature)*](https://doi.org/10.1038/s41598-025-26910-4) |
| **On-device AI for climate-resilient farming with intelligent crop yield prediction using lightweight models (2023)** | Lightweight ML on Edge Devices (Deploys low-computation algorithms on smart sensors for real-time inference) | Localized Indian sensor data | Limited computational capacity on-device. | Expanding the model to support drone integration. | [*Scientific Reports (Nature)*](https://doi.org/10.1038/s41598-025-16014-4) |
| **Non-destructive yield estimation of onion and garlic using UAV-based hyperspectral imaging and hybrid machine learning models (2023)** | UAV Hyperspectral Imaging, Hybrid ML (Combines drone spectral imaging with machine learning for non-invasive yield tracking) | Global agricultural hyperspectral image datasets | Extremely high hardware cost for farmers. | Developing satellite-based low-cost alternatives. | [*BMC Plant Biology*](https://doi.org/10.1186/s12870-026-09289-w) |

#### Year: 2024
| Paper Title | Methodology & Algorithm / Technique | Dataset | Limitation | Future Scope | Source / Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **An explainable AI-based hybrid machine learning model for interpretability and enhanced crop yield prediction (2024)** | Hybrid ML (Random Forest, XGBoost), XAI (Merges ensemble methods with explainable AI for high interpretability) | Indian soil and crop yield statistics | Struggles with unstructured meteorological data. | Integrating real-time weather forecasting APIs. | [*MethodsX (Elsevier)*](https://doi.org/10.1016/j.mex.2025.103442) |
| **Enhancing precision agriculture through cloud based transformative crop recommendation model (2024)** | Cloud-based ML Framework (Processes massive digitized Soil Health Card datasets using scalable cloud infrastructure) | Regional Soil Health Card data | Latency issues in rural areas with poor internet. | Shifting to fog/edge computing architectures. | [*Scientific Reports (Nature)*](https://doi.org/10.1038/s41598-025-93417-3) |
| **Maize yield prediction using machine learning: a systematic literature review (2024)** | Meta-Analysis & Review of ML Algorithms (Systematically evaluates various predictive models across historical data) | Global historical maize yield data | Highlights lack of standardization in ML metrics. | Creating an open-source standard agricultural dataset. | [*Frontiers in Artificial Intelligence*](https://doi.org/10.3389/frai.2026.1735157) |

#### Year: 2025
| Paper Title | Methodology & Algorithm / Technique | Dataset | Limitation | Future Scope | Source / Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Soil test crop response based fertilizer calibration and soil nutrient forecasting for aerobic rice on Alfisols (2025)** | Soil Test Crop Response (STCR), ML (Integrates traditional agronomic equations with modern forecasting algorithms) | Alfisols datasets from Southern India | Highly specific to Alfisol soil types. | Expanding the calibration framework to all soil types. | [*Scientific Reports (Nature)*](https://doi.org/10.1038/s41598-026-48172-4) |
| **Agentic AI-driven autonomous decision support system for smart agriculture (2025)** | Agentic AI, Autonomous Decision Trees (Deploys autonomous agents that make decisions without continuous human input) | Live IoT sensor arrays in Indian test farms | High setup complexity and maintenance. | Developing zero-configuration autonomous agents. | [*Scientific Reports (Nature)*](https://doi.org/10.1038/s41598-026-39472-w) |
| **Regional machine learning-based estimation of methane emissions from rice cultivation (2025)** | Spatial ML, Emission Modeling (Utilizes geospatial modeling coupled with ML to track and predict greenhouse emissions) | South Korean regional emission datasets | Not calibrated for tropical climates. | Global multi-climate emission tracking. | [*Scientific Reports (Nature)*](https://doi.org/10.1038/s41598-026-49883-4) |

#### Year: 2026
| Paper Title | Methodology & Algorithm / Technique | Dataset | Limitation | Future Scope | Source / Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **An evaluation of machine learning for soil analysis in internet of things-enabled smart farming (2026)** | Evaluation of IoT-ML Pipelines (Benchmarks the end-to-end performance of physical sensors streaming data into ML models) | NPK sensor logs from smart farms | Sensor drift causes long-term accuracy decay. | Auto-calibrating ML models for sensor degradation. | [*Scientific Reports (Nature)*](https://doi.org/10.1038/s41598-026-36017-z) |
| **Towards enhancing the performance of crop prediction system for precision agriculture using feature correlation (2026)** | Feature Correlation Square-based KNN (Uses advanced statistical correlation metrics to improve K-Nearest Neighbor predictions) | Comprehensive Indian agro-climatic datasets | Computationally heavy for large feature spaces. | Quantum-inspired optimization algorithms. | [*Scientific Reports (Nature)*](https://doi.org/10.1038/s41598-026-35212-2) |
| **Enhancing precision nitrogen management in corn through integration of soil properties and remote sensing (2026)** | Mechanistic Approach, Remote Sensing (Combines physical soil property science with large-scale satellite imagery data) | Global satellite and ground-truth corn data | Complex integration of multi-modal data. | Fully automated drone-to-tractor nitrogen delivery. | [*Science of The Total Environment (Elsevier)*](https://doi.org/10.1016/j.scitotenv.2026.181853) |

---

### 2. Research Gap

*   **Current Systems (Indian Context):** Most current systems deployed in India rely on static datasets (like historical Soil Health Cards) to provide **"Predict Only"** recommendations (e.g., standard NPK doses). They lack real-time adaptability to erratic monsoons and operate as "black boxes" which limits adoption among local farmers. 
*   **Proposed System:** **Predict + Simulate Future Scenarios**. By combining **Explainable AI (XAI)** and localized **Digital Twin** concepts, the proposed system will not only recommend fertilizers but also simulate "what-if" scenarios (e.g., "How will a delayed monsoon affect the current fertilizer dosage?"). It will provide transparent reasoning in regional contexts, bridging the gap between advanced global AI techniques and local smallholder farming needs.

---

## Output: Survey Paper Draft

### 1. Introduction
The agricultural sector is the backbone of the Indian economy, yet it faces immense challenges due to climate unpredictability, soil degradation, and fragmented landholdings. While the government's Soil Health Card scheme has provided vast amounts of soil data, traditional fertilizer recommendation methods remain largely static. Between 2023 and 2026, the integration of Machine Learning (ML) and Artificial Intelligence (AI) has begun transforming this landscape. This survey explores recent advancements in nutrient recommendation systems, focusing on the transition from static predictive models to dynamic, transparent, and simulation-capable frameworks (like Agentic AI and XAI) tailored for the Indian agricultural ecosystem.

### 2. Related Work
Recent literature highlights a rapid shift toward data-driven agriculture in India. Studies have successfully utilized interpretable deep learning models to predict crop and fertilizer requirements using regional Indian soil datasets [1]. The rise of Agentic AI-driven autonomous decision support systems has enabled continuous advisory for rural farmers [8]. However, researchers have identified the "black-box" nature of algorithms as a significant barrier to trust [4]. Consequently, global and regional focus has shifted towards Explainable AI (XAI) tools to clarify the reasoning behind specific fertilizer dosages. Furthermore, cutting-edge research introduced IoT-enabled smart farming evaluations to optimize resource allocation dynamically [10].

### 3. Comparative Analysis
A critical comparison of recent methodologies reveals a trade-off between predictive accuracy, model interpretability, and local applicability:
*   **Traditional ML vs. Agentic AI:** While ML models effectively process numerical soil data, Agentic AI models excel at translating these insights into actionable, continuous advice for farmers. 
*   **Black-box vs. XAI:** Standard models output a single nutrient dose without explanation. Systems employing XAI significantly improve stakeholder trust by detailing exactly how much influence nitrogen or pH had on the recommendation.
*   **Static vs. Dynamic (IoT & Sensors):** Most Indian recommendation systems are static. Conversely, IoT-integrated models provide a continuous, real-time feedback loop, though adapting them for smallholder Indian farms remains a challenge due to hardware costs.

### 4. Research Gap
Despite significant progress, a substantial research gap persists in the Indian context. **Current systems are strictly predictive and static.** They successfully recommend nutrients based on existing datasets but fail to provide interactive, forward-looking simulations adaptable to local climatic shocks. 
The proposed solution must evolve from a **"Predict Only"** model to a **"Predict + Simulate Future Scenarios"** framework, synergizing Agentic AI with Explainable AI.

### 5. References
1. *Interpretable deep learning models for independent fertilizer and crop recommendation.* Scientific Reports (Nature). DOI: 10.1038/s41598-025-26910-4
2. *On-device AI for climate-resilient farming with intelligent crop yield prediction using lightweight models on smart agricultural devices.* Scientific Reports (Nature). DOI: 10.1038/s41598-025-16014-4
3. *Non-destructive yield estimation of onion and garlic using UAV-based hyperspectral imaging and hybrid machine learning models.* BMC Plant Biology. DOI: 10.1186/s12870-026-09289-w
4. *An explainable AI-based hybrid machine learning model for interpretability and enhanced crop yield prediction.* MethodsX (Elsevier). DOI: 10.1016/j.mex.2025.103442
5. *Enhancing precision agriculture through cloud based transformative crop recommendation model.* Scientific Reports (Nature). DOI: 10.1038/s41598-025-93417-3
6. *Maize yield prediction using machine learning: a systematic literature review.* Frontiers in Artificial Intelligence. DOI: 10.3389/frai.2026.1735157
7. *Soil test crop response based fertilizer calibration and soil nutrient forecasting for aerobic rice on Alfisols of Southern India.* Scientific Reports (Nature). DOI: 10.1038/s41598-026-48172-4
8. *Agentic AI-driven autonomous decision support system for smart agriculture.* Scientific Reports (Nature). DOI: 10.1038/s41598-026-39472-w
9. *Regional machine learning-based estimation of methane emissions from rice cultivation in South Korea.* Scientific Reports (Nature). DOI: 10.1038/s41598-026-49883-4
10. *An evaluation of machine learning for soil analysis in internet of things-enabled smart farming.* Scientific Reports (Nature). DOI: 10.1038/s41598-026-36017-z
11. *Towards enhancing the performance of crop prediction system for precision agriculture using feature correlation square-based nearest neighbor classifier.* Scientific Reports (Nature). DOI: 10.1038/s41598-026-35212-2
12. *Enhancing precision nitrogen management in corn through integration of soil properties and remote sensing: A mechanistic approach.* Science of The Total Environment (Elsevier). DOI: 10.1016/j.scitotenv.2026.181853
