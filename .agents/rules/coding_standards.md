# Engineering & Coding Standards for AI Agents

This document defines the strict engineering standards, architectural boundaries, and verification requirements for all autonomous and assisted agents operating within this workspace.

---

## 1. Architectural Boundaries & Modularity

- **Strict Layer Separation**:
  - **API Layer (`backend/api/`)**: Defines HTTP routes, input validation, status codes, and endpoint documentation. Must NOT contain heavy business logic or raw SQL queries.
  - **Service Layer (`backend/services/`)**: Encapsulates core business logic, third-party API clients, and orchestration between domain models and external systems.
  - **Schema Layer (`backend/schemas/`)**: Houses Pydantic V2 models for request/response serialization. All data crossing API boundaries must be strongly typed.
  - **ML Layer (`backend/ml/`)**: Contains training pipelines, feature engineering, and inference modules (`backend/ml/inference/`). Inference modules must load trained model artifacts (e.g. `.joblib`) lazily or at initialization with graceful fallbacks.
  - **Frontend (`frontend_web/`)**: Clear separation between app router pages (`src/app/`), UI components (`src/components/`), state contexts (`src/context/`), and API helpers.

- **Single Responsibility Principle**:
  - Keep modules focused on a single responsibility.
  - Avoid monolithic files; decompose complex functions into composable, testable helpers.

---

## 2. Strong Typing & Schema Enforcement

- **Python (Backend)**:
  - Enforce explicit type hints on all public functions, classes, and return signatures.
  - Use Pydantic V2 models for request validation and response formatting.
  - Avoid Pydantic protected namespace conflicts (e.g., prefix fields with `version` or domain names rather than reserved prefixes like `model_`).
  - Prohibit bare `dict` or untyped `Any` payloads across system boundaries.

- **TypeScript (Frontend)**:
  - Strict mode enabled; no implicit `any`.
  - Maintain explicit TypeScript types matching backend response schemas.

---

## 3. Automated Verification & Testing

Every implementation or modification must pass automated verification before completion:

1. **Syntax & Import Validation**:
   - Verify syntax via static analysis or compilation check (e.g., `python -m py_compile <file>`).
   - Confirm that modified modules import cleanly without circular dependency errors or runtime syntax issues.

2. **Regression & Unit Verification**:
   - Run relevant test suites or smoke-test scripts against modified endpoints or ML inference pipelines.
   - For ML models, always verify inference with test inputs, validate output shape, and ensure inverse transformations produce expected domain labels.

3. **No Unverified Claims**:
   - Agents must never assume a script, build, or endpoint succeeds without inspecting command exit codes and actual execution outputs.

---

## 4. Error Handling & Resilient Fallbacks

- **Graceful Degradation**:
  - External network calls (weather APIs, LLM providers, geocoding) must implement timeouts and fall back to local cached data or regional baselines.
  - ML inference pipelines must gracefully handle missing artifacts or missing features via imputers or baseline models.

- **Explicit Exceptions**:
  - Never catch and silence generic exceptions (`except Exception: pass`). Always log failures with context and raise appropriate HTTP exceptions (`HTTPException` with informative error codes and details).

---

## 5. Security & Environment Integrity

- **Environment Variables**:
  - Sensitive keys (`DATABASE_URL`, API keys) must be loaded from `.env` or system environment via `backend/core/config.py`. Never hardcode secrets.
- **Data Loss Prevention**:
  - Always obtain confirmation before running destructive operations (dropping databases, purging tables, or force-deleting production files).

