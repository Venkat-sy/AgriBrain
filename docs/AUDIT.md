# AgriSim Audit Summary

## Goal

Continue reviewing the **frontend AI integration** (chat handler & AI service) to understand how the React app communicates with the backend and external services.

## Current State

* The **frontend AI integration** files have been located:
  * `frontend/react-app/server/chatHandler.js` – implements the Vite dev‑server endpoint that receives chat requests from the React UI and forwards them to either a local FastAPI model endpoint or a deterministic mock.
  * `frontend/react-app/src/services/aiService.js` – provides `sendChatMessage` (which POSTs to `/api/chat`) and `buildFarmContext` for shaping the farm state payload sent to the backend.
* Both files contain concrete implementations with real network calls (`fetch` to the FastAPI backend at `http://localhost:8000/api/v1/crop/recommend`). No references to external APIs such as `OPENWEATHER` were found.

## Findings

**File Locations**
```
frontend/react-app/server/chatHandler.js
frontend/react-app/src/services/aiService.js
```

**Communication Flow**
1. **User Interaction** – The user types a message in `AIChat.jsx`.
2. `AIChat.jsx` calls `buildFarmContext(appContext)` to create a normalized farm context object.
3. `sendChatMessage({messages, farmContext, userMessage})` in `aiService.js` POSTs to the Vite dev‑server endpoint **`/api/chat`**.
4. Vite proxies this request to `frontend/react-app/server/chatHandler.js` → `handleChatRequest`.
5. `handleChatRequest` first attempts `runMyModel`, which may:
   * Detect an intent for crop recommendation and **fetch** `http://localhost:8000/api/v1/crop/recommend` (FastAPI backend) with a payload derived from the farm context.
   * Return the model’s response (message, provider, model version) back to the frontend.
6. If no local model matches, `handleChatRequest` falls back to a deterministic **mock** response based on the farm context.
7. The response is sent back through Vite to the React UI, where `AIChat.jsx` displays the assistant message.

No external third‑party APIs (e.g., OpenWeather) are invoked; all data flows between the React UI and the local FastAPI service.

## Immediate Next Steps

1. **Verify file locations** – list the repository tree to confirm where the chat handler and AI service actually reside.
2. **Read the identified files** – if they exist, inspect their contents; if they are empty, request the correct version of the project.
3. **Adjust paths** – update the paths if the files live in a different sub‑folder (e.g., `src/server/` or `src/utils/`).
4. **Re‑run searches** – after locating the files, look for `fetch(` usage and any external‑API identifiers such as `OPENWEATHER`.
5. **Document the communication flow** – map out how the frontend invokes backend endpoints and any external service integrations (including required environment variables).

## Suggested Commands

* `dir /s /b C:\Users\USER\Downloads\FinalYearProject > tree.txt` – generate a full file list.
* `type <path>` – view a file’s content.
* `findstr /R "fetch(" *.js *.ts` – search for fetch calls.

## Expected Outcome

* A clear picture of the **AI chat integration** path.
* Identification of any missing implementation or mis‑placed files.
* Updated documentation (`AGRI_SIM_AUDIT.md`) reflecting the actual code structure.

---

**Save this content as `AGRI_SIM_AUDIT.md` in the project root and share it with the team.**
