Here is the absolute, ground-level, file-by-file technical specification. There is no high-level overview here. This is the exact pin-to-pin data contract, state management, and logic flow your coding agent needs to write the code without guessing.

Copy this entire block and save it as `AGRIBRAIN_STRICT_SPEC.txt`. Tell your agent: **"Read this strict spec. Build the files exactly to these data contracts and logic steps."**

```text
# AGRIBRAIN: STRICT PIN-TO-PIN TECHNICAL SPECIFICATION

## 1. DATA CONTRACTS (PYDANTIC SCHEMAS)
File: `backend/schemas/simulation.py`
The agent must strictly use these models for the Digital Twin API. Do not invent fields.

class SimulationRequest(BaseModel):
    lat: float
    lng: float
    setup_type: str = Field(..., description="Must be 'short-term' or 'long-term'")

class TimelineStage(BaseModel):
    stage_name: str
    estimated_days: int
    agronomy_advice: str

class SimulationResponse(BaseModel):
    district: str
    soil_n: float
    soil_p: float
    soil_k: float
    soil_ph: float
    live_temp: float
    live_humidity: float
    live_rainfall: float
    recommended_crop: str
    confidence_score: float
    cultivation_timeline: List[TimelineStage]

## 2. FRONTEND: MAP PINPOINTING & STATE INJECTION
File: `frontend_web/src/components/MapUI.tsx`

**Strict Logic Flow:**
1. Import `MapContainer`, `TileLayer`, `Marker`, `useMapEvents` from `react-leaflet`.
2. Define props: `{ onPinDrop: (lat: number, lng: number) => void }`.
3. Create an internal component `<MapClickHandler />`:
   ```javascript
   const MapClickHandler = ({ onPinDrop }) => {
     useMapEvents({
       click(e) {
         onPinDrop(e.latlng.lat, e.latlng.lng);
       },
     });
     return null;
   };

```

4. Do NOT await GeoJSON fetch to allow clicking. The click listener must be active immediately.

## 3. FRONTEND: SIMULATION PAGE & API WIRING

File: `frontend_web/src/app/simulate/page.tsx`

**Strict Logic Flow:**

1. State hooks required:
* `const [pin, setPin] = useState<{lat: number, lng: number} | null>(null);`
* `const [setupType, setSetupType] = useState<"short-term" | "long-term">("short-term");`
* `const [loading, setLoading] = useState(false);`
* `const [results, setResults] = useState<SimulationResponse | null>(null);`
* `const [error, setError] = useState<string | null>(null);`


2. `handlePinDrop` function: Instantly sets `pin` state.
3. `runSimulation` function:
* Triggers on button click after pin is dropped.
* Sets `loading(true)`, `error(null)`.
* `fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/simulation/run`, { method: "POST", body: JSON.stringify({ lat: pin.lat, lng: pin.lng, setup_type: setupType }) })`
* Wrap in `try/catch`. Catch block must `setError(err.message)`.


4. UI requires a toggle switch for `setupType` ("Short-term Farm" vs "Long-term Orchard").

## 4. BACKEND: SIMULATION ORCHESTRATOR

File: `backend/api/simulation.py`

**Endpoint:** `@router.post("/run", response_model=SimulationResponse)`
**Strict Logic Flow (Must execute in this exact order):**

1. **Reverse Geocode (Nominatim Fallback):**
* `requests.get(f"https://nominatim.openstreetmap.org/reverse?format=json&lat={req.lat}&lon={req.lng}", headers={"User-Agent": "AgriBrain/1.0"})`
* Extract `district = data.get("address", {}).get("state_district", "Unknown")`.


2. **Fetch Weather (IndianAPI):**
* `requests.get(f"https://weather.indianapi.in/india/weather?city={district}", headers={"Authorization": os.getenv("WEATHER_API_KEY")})`
* Extract `temp`, `humidity`, `rainfall`. If API fails, default to temp=28.0, humidity=65.0, rainfall=100.0.


3. **Fetch Soil Baseline:**
* Query local dataset/DB for average N, P, K, pH for `district`. If not found, use India-wide averages (N=150, P=20, K=120, pH=6.5).


4. **XGBoost Inference:**
* Construct numpy array: `features = np.array([[soil_n, soil_p, soil_k, soil_ph, temp, humidity, rainfall]])`.
* `probs = xgboost_model.predict_proba(features)[0]`
* Get top 3 crops using `np.argsort(probs)[-3:][::-1]`.


5. **Apply Setup Type Filter:**
* Define sets: `LONG_TERM_CROPS = {"apple", "banana", "papaya", "coconut", "grapes", "orange"}`.
* If `req.setup_type == "short-term"`: Iterate top 3 crops, pick the first one NOT in `LONG_TERM_CROPS`.
* If `req.setup_type == "long-term"`: Iterate top 3 crops, pick the first one IN `LONG_TERM_CROPS`. (Fallback to highest probability if no match).


6. **Generate LLM Timeline (Groq):**
* Initialize `client = Groq(api_key=os.getenv("GROQ_API_KEY"))`.
* Prompt: `"Generate a cultivation timeline for {final_crop} in {district} with {soil_type} soil. Return strictly a JSON array of objects with keys: stage_name, estimated_days, agronomy_advice."`
* Parse JSON response.


7. **Return Payload:** Construct and return the `SimulationResponse` model.

## 5. BACKEND: VISION CHATBOT (MULTIMODAL)

File: `backend/api/chat.py`

**Endpoint:** `@router.post("/troubleshoot")`
**Strict Logic Flow:**

1. Endpoint signature MUST use `UploadFile` for images and `Form` for text:
`async def troubleshoot_chat(message: str = Form(...), file: UploadFile = File(None)):`
2. **Image Processing (if file exists):**
* `file_bytes = await file.read()`
* `base64_image = base64.b64encode(file_bytes).decode("utf-8")`
* Set Groq model to `"llama-3.2-11b-vision-preview"`.
* Construct Groq payload:
```python
messages=[{
    "role": "user",
    "content": [
        {"type": "text", "text": message},
        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
    ]
}]

```




3. **Text-Only Processing (if no file):**
* Set Groq model to `"llama3-8b-8192"`.
* Construct standard messages: `[{"role": "user", "content": message}]`.


4. Execute `client.chat.completions.create(...)` and return the `content` string.

## 6. CSS / TAILWIND MOBILE BREAKPOINTS

All container elements MUST use these exact breakpoints to prevent mobile overflow:

* Main Page Container: `min-h-screen w-full flex flex-col md:flex-row p-2 md:p-4`
* Map Container: `w-full h-[50vh] md:h-[600px] rounded-lg overflow-hidden relative z-0`
* Sidebar/Results Container: `w-full md:w-1/3 flex-shrink-0 mt-4 md:mt-0`

```

```