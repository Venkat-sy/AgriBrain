# Project Progress Tracker: Comprehensive Report

This document serves as a detailed, week-by-week progress tracker for the final year project. It comprehensively documents all tasks, architectural decisions, feature implementations, and challenges addressed throughout the project lifecycle.

---

## Week 1 (June 16, 2026 - June 22, 2026)

**Key Tasks Completed**
- **Project Initialization & Scope Definition:** Successfully initialized the local repository and set up version control. Defined the initial scope of the project, focusing on integrating machine learning with agricultural data to provide actionable insights for crop yield and soil health.
- **Architectural Planning:** Drafted the initial comprehensive Project Roadmap and Architecture Guide. This document outlined the proposed technology stack (HTML/CSS/JS frontend, Python/ML backend) and the phased approach to development.
- **Stage 1 Literature Survey:** Conducted an extensive preliminary literature review, gathering context specifically tailored for Indian agriculture and local datasets. 
- **Resource Gathering:** Developed a curated Resource Vault. This vault focused exclusively on Indian accessibility, utilizing un-gated platforms and open-access journals to ensure the research was reproducible and accessible without expensive academic subscriptions.
- **Data Generation:** Since real-world data was still being sourced, generated a robust synthetic Indian Soil Health dataset containing 10,000 rows. This allowed the initial exploratory data analysis (EDA) and pipeline testing to begin immediately.
- **Study Materials:** Created specialized cheat sheets for self-study, mentor meetings, and upcoming viva/defense preparations to ensure complete understanding of the domain.

**Features Added or Modified**
- **Datasets:** Generated `data/soil_health_data.csv` via a new, custom Python script `data/generate_dataset.py`.
- **Notebooks:** Added the foundational exploratory data analysis (EDA) notebook `notebooks/eda_and_preprocessing.ipynb` to begin analyzing the synthetic data distributions.
- **Documentation:** Added `PROJECT_ROADMAP.md`, `STAGE_1_Survey.md`, `STAGE_1_Resource_Vault.md`, and `STAGE_1_CheatSheet.md`.

**Challenges Faced & Resolutions**
- **Challenge:** A significant number of initial resource links discovered during research were broken, paywalled, or geographically restricted.
- **Resolution:** Systematically replaced dead links with exact YouTube URLs, open-access PDFs, and foolproof search queries. Localized all resources to ensure they were relevant to the Indian agricultural context.

**Relevant Commits / Files**
- Initial commit: `cfe25b3`
- Dataset generation: [generate_dataset.py](file:///c:/Users/USER/Downloads/FinalYearProject/data/generate_dataset.py) (Commit `b75fa1e`)
- Roadmap creation: [PROJECT_ROADMAP.md](file:///c:/Users/USER/Downloads/FinalYearProject/PROJECT_ROADMAP.md) (Commit `15ee8d2`)

---

## Week 2 (June 23, 2026 - June 29, 2026)

**Key Tasks Completed**
- **Offline Algorithm Research:** Dedicated this week entirely to offline research, focusing on the theoretical underpinnings of various machine learning algorithms suitable for tabular agricultural data. 
- **Academic Deep-Dive:** Read and annotated several complex research papers regarding crop yield prediction and soil health risk assessment, identifying the methodologies that yielded the highest accuracy in similar studies.
- **Mentor Consultations:** Prepared materials and questions for mentor reviews, refining the project's direction based on academic requirements and ensuring the proposed ML solutions were viable for a final year project scope.

*Note: No major codebase changes were pushed during this week as the focus was strictly on theoretical foundation and methodology planning.*

---

## Week 3 (June 30, 2026 - July 6, 2026)

**Key Tasks Completed**
- **Literature Survey Refactoring:** Restructured the literature survey to meet strict academic guidelines. Implemented a rigid framework requiring exactly 2 Indian papers and 1 International paper per year to ensure a balanced, geographically relevant perspective.
- **Survey Explanations:** Wrote detailed, paragraph-length explanations and summaries for each of the 12 extracted surveys, highlighting their methodologies, datasets used, and limitations.
- **Frontend Prototyping:** Designed and implemented the first iteration of the UI blueprint for the frontend application. This involved establishing the basic HTML skeletal structure and applying initial CSS styling to create a clean, accessible layout for agricultural users.
- **CI/CD Pipeline Setup:** Configured continuous deployment (CI/CD) to automatically deploy the frontend application to GitHub Pages whenever changes are pushed to the main branch.

**Features Added or Modified**
- **Frontend UI:** Added the foundational HTML and CSS structures (`frontend/index.html`, `frontend/styles.css`).
- **CI/CD:** Created a GitHub Action workflow (`.github/workflows/static.yml`) for seamless, automated deployments.
- **Documentation:** Added `STAGE_1_Survey_Explanations.md` containing the deep-dive academic summaries.

**Challenges Faced & Resolutions**
- **Challenge:** Finding a reliable, free way to host the static frontend so that stakeholders and mentors could view real-time progress without running the code locally.
- **Resolution:** Successfully researched, configured, and triggered GitHub Pages deployment via custom GitHub Actions, creating an automated pipeline.

**Relevant Commits / Files**
- UI Blueprint: [index.html](file:///c:/Users/USER/Downloads/FinalYearProject/frontend/index.html) (Commit `afb0c93`)
- GitHub Action: [static.yml](file:///c:/Users/USER/Downloads/FinalYearProject/.github/workflows/static.yml) (Commit `abd0a8e`)

---

## Week 4 (July 7, 2026 - July 13, 2026)

**Key Tasks Completed**
- **Academic Rigor Overhaul:** Completely rewrote the literature surveys using 100% verified real Scispace papers, ensuring every entry had a full, verifiable academic DOI.
- **Major UI Redesign (Glassmorphism):** Executed a comprehensive overhaul of the frontend UI. Transitioned to a modern "glassmorphism" aesthetic to give the application a premium, high-tech feel. Implemented a Single Page Application (SPA) architecture with Digital Twin demo screens.
- **Reference Layout Matching:** Painstakingly refined the UI CSS to exactly match a provided reference image layout, ensuring pixel-perfect alignment and professional presentation.
- **Interactive Components:** Developed and integrated interactive NPK (Nitrogen, Phosphorus, Potassium) sliders and dummy SPA navigation tabs into the frontend, preparing the UI for backend ML integration.
- **Stage 2 Data Integration:** Uploaded the finalized Stage 2 advanced agriculture dataset, alongside advanced EDA scripts and high-quality output charts for the final report.

**Features Added or Modified**
- **Frontend UI:** Major updates to `frontend/index.html` and `frontend/styles.css` incorporating complex CSS styling, interactive NPK sliders, and a digital twin interface.
- **Datasets & EDA:** Added the refined `data/advanced_agri_dataset.csv` (10,000 rows) and `data/preprocessed_agri_data.csv`.
- **Scripts:** Added `notebooks/eda_and_preprocessing.py` and a utility script `fix_header.py`.
- **Outputs:** Uploaded detailed analysis charts including `output/correlation_heatmap.png`, `output/risk_distribution.png`, and `output/yield_distribution.png`.
- **Literature Data:** Added structured JSON dumps of research papers (`epmc_papers.json`, `papers.json`) for programmatic access.

**Challenges Faced & Resolutions**
- **Challenge:** Ensuring the absolute credibility of the literature survey to pass rigorous academic review.
- **Resolution:** Transitioned exclusively to highly reputed journals, manually verifying full academic citations and DOIs via the Scispace platform.
- **Challenge:** Creating a modern, premium look for the application that stands out from typical academic projects.
- **Resolution:** Implemented a complex glassmorphism design system utilizing CSS backdrops and translucency to elevate the UI's aesthetic appeal.

**Relevant Commits / Files**
- Stage 2 Dataset & EDA: [advanced_agri_dataset.csv](file:///c:/Users/USER/Downloads/FinalYearProject/data/advanced_agri_dataset.csv) (Commit `83afdd5`)
- UI Redesign: [index.html](file:///c:/Users/USER/Downloads/FinalYearProject/frontend/index.html) (Commits `8721a5b`, `f02e063`, `6b85c20`)
- Verified Papers: `epmc_papers.json` (Commit `19c8176`)

---

## Week 5 (July 14, 2026 - July 20, 2026)

**Key Tasks Completed**
- **Algorithm Comparative Analysis:** Conducted an in-depth, offline evaluation of viable machine learning algorithms for agricultural tabular data. Compared the theoretical performance of Random Forest, XGBoost, and standard Neural Networks regarding their handling of non-linear agricultural features.
- **Feature Importance Profiling:** Analyzed dataset features mathematically to identify the most predictive variables for crop yield and soil risk (e.g., mapping the specific weight of Potassium vs. pH levels).
- **Backend Architecture Planning:** Drafted the initial backend architecture plan. Defined how the Python ML models would eventually be wrapped in a REST API framework (like Flask or FastAPI) to connect with the frontend SPA endpoints.

**Challenges Faced & Resolutions**
- **Challenge:** Selecting a model that balances high predictive accuracy with "explainability" (a common requirement in agricultural tech so farmers trust the AI).
- **Resolution:** Decided to prioritize tree-based ensemble models (like Random Forest and XGBoost) over opaque Neural Networks, as tree models are highly compatible with SHAP analysis for later explainability.

---

## Week 6 (July 21, 2026 - July 27, 2026)

**Key Tasks Completed**
- **Advanced Data Preprocessing:** Processed the `advanced_agri_dataset.csv` offline. Applied rigorous techniques to handle any edge-case missing values via imputation, normalized continuous variables using standard scaling, and encoded categorical data (like soil types) using one-hot encoding methodologies.
- **Multicollinearity Checks:** Explored deep correlation matrices to detect and avoid multicollinearity among NPK values, pH levels, and environmental factors like rainfall and temperature, ensuring the model wouldn't double-count correlated features.
- **Stratified Sampling:** Prepared the train-test split strategies. Implemented stratified sampling to ensure a perfectly balanced representation across diverse and rare crop types in both the training and testing datasets.

---

## Week 7 (July 28, 2026 - August 3, 2026)

**Key Tasks Completed**
- **Environment Standardization:** Set up the isolated local Python virtual environment to ensure the project is reproducible on other machines. Systematically resolved deep dependency conflicts between various data science packages.
- **Baseline Model Drafting:** Wrote the initial scripts to train baseline, unoptimized ML models (like simple Decision Trees). This was crucial to establish a "floor" benchmark accuracy score that more complex models must beat.
- **Pipeline Documentation:** Meticulously documented all data pipelines and offline preprocessing steps. This documentation is being prepared for direct inclusion in the final project thesis report.

**Challenges Faced & Resolutions**
- **Challenge:** Encountered library version conflicts between standard ML packages (scikit-learn) and explainability tools (SHAP) leading to execution errors.
- **Resolution:** Conducted isolation testing to find compatible versions, standardizing them into a unified `requirements.txt` draft to prevent future environment breaks.

---

## Week 8 (August 4, 2026 - August 10, 2026)

**Key Tasks Completed**
- **Hyperparameter Tuning:** Conducted extensive hyperparameter tuning for the baseline models. Utilized GridSearchCV techniques to test hundreds of combinations of tree depths, learning rates, and estimator counts to squeeze out maximum accuracy.
- **Validation Evaluation:** Evaluated early model performance on strict, unseen validation sets, recording metrics such as accuracy, precision, recall, and F1-scores for the project report.
- **UI/UX Output Visualization Planning:** Reviewed and sketched out UI/UX improvements for the frontend. Planned exactly how the complex numerical model outputs (like expected yield tons/hectare and risk factor percentages) will be translated into user-friendly visual alerts on the web page.

---

## Week 9 (August 11, 2026 - August 17, 2026)

**Key Tasks Completed**
- **Final Model Selection:** Finalized the ultimate model selection based on the rigorous validation metrics gathered in the previous week, locking in the algorithm architecture.
- **Script Modularization:** Began cleanly structuring and modularizing the Python code into `train_models.py` and `shap_analysis.py`. This ensures the code is maintainable and ready for integration into the main Git repository.
- **API Contract Design:** Designed the strict REST API JSON contract. Documented exactly what JSON payloads the frontend NPK sliders will send to the backend, and exactly what schema the backend will return with the predictions.

---

## Week 10 (August 18, 2026 - August 24, 2026)

**Key Tasks Completed**
- **Active ML Development:** Actively developed and executed the finalized machine learning training scripts, saving the persistent, trained model weights locally.
- **Explainable AI (XAI) Implementation:** Implemented SHAP (SHapley Additive exPlanations) analysis scripts. This crucial feature adds transparency to the predictive models, allowing the system to output exactly *why* a certain crop yield was predicted based on the specific inputs.
- **Frontend Interactivity Updates:** Updated the frontend HTML and CSS to accommodate the new backend ML capabilities, preparing loading states, error boundaries, and visualization containers for the SHAP outputs.

**Features Added or Modified**
- **Machine Learning:** Created the core model training scripts (`train_models.py`) and explainability analysis scripts (`shap_analysis.py`).
- **Environment:** Finalized updates to `requirements.txt` incorporating all necessary, version-locked ML libraries.
- **Frontend UI:** Modified `frontend/index.html` and `frontend/styles.css` for enhanced DOM interactivity.
- **Data Management:** Established structured local directories for `datasets/` and `training_data/`.

**Challenges Faced & Resolutions**
- **Challenge:** AI model outputs are often "black boxes," making it incredibly hard for end-users (farmers/agronomists) to trust the predictions.
- **Resolution:** Integrated cutting-edge SHAP analysis to provide clear, visual feature importance breakdowns for every single prediction made by the system.

**Relevant Commits / Files**
- ML Scripts: [train_models.py](file:///c:/Users/USER/Downloads/FinalYearProject/train_models.py) (Uncommitted local work)
- Explainability: [shap_analysis.py](file:///c:/Users/USER/Downloads/FinalYearProject/shap_analysis.py) (Uncommitted local work)

---

## Week 11 (August 25, 2026 - Present)

**Key Tasks Completed**
- **Documentation Overhaul:** Conducted a comprehensive assessment of all project progress to date. Generated this highly detailed, academic-grade week-by-week documentation (`progress.md`) to reflect the true depth of work completed.
- **Copilot Integration Setup:** Attempted the setup and configuration of OmniRoute and local AI copilot tools (like OpenCode) to accelerate the final phases of backend API development and frontend integration.

**Pending Tasks / Next Steps**
- **Resolve Configuration Issues:** Troubleshoot and resolve the OmniRoute local server timeouts and configuration errors.
- **API Integration:** Proceed with building the Python REST API server and connecting the frontend UI interface to the trained ML models.
- **Version Control Update:** Commit and push all recent local machine learning scripts, datasets, and documentation updates to the GitHub repository.