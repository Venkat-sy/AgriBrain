# AgriBrain - AgriSim ML Validation Dashboard

A Streamlit-based validation dashboard for testing AgriSim ML models, simulation engine, and SHAP explainability against a FastAPI backend.

## 🚀 Features

- **Interactive Simulation Parameters**: 9 input sliders (N, P, K, pH, temperature, humidity, rainfall, budget, land area) + optional district/state
- **Real-time ML Inference**: Calls FastAPI backend for crop recommendation, yield prediction, risk assessment
- **SHAP Explainability**: Horizontal bar chart visualization of feature impact (green=positive, red=negative)
- **Financial Projections**: ROI, net profit, market value, total cost breakdown
- **Risk Assessment**: Gauge charts for yield and ROI, risk factor analysis
- **Crop Growth Timeline**: Phase-by-phase cultivation activities
- **AI Chat Assistant**: Context-aware troubleshooting chat powered by Gemini
- **Session Management**: Persistent chat history and simulation context

## 📦 Quick Start (Local Development)

### Prerequisites
- Python 3.9+
- FastAPI backend running on `http://localhost:8000`

### Installation

```bash
# Clone the repository
git clone https://github.com/Venkat-sy/AgriBrain.git
cd AgriBrain

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install streamlit plotly python-dotenv
```

### Run the Dashboard

```bash
# Terminal 1: Start FastAPI backend (required)
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Start Streamlit dashboard
cd frontend_streamlit
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

## ☁️ Streamlit Cloud Deployment

### 1. Push to GitHub
```bash
git add .
git commit -m "Add Streamlit validation dashboard"
git push origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your repository: `Venkat-sy/AgriBrain`
4. Set branch: `main`
5. Set main file path: `frontend_streamlit/app.py`
6. Click "Deploy!"

### 3. Configure Secrets (Streamlit Cloud Dashboard)
In Streamlit Cloud app settings → Secrets, add:
```toml
API_BASE_URL = "https://your-fastapi-backend-url.com"
```

> **Note**: The FastAPI backend must be deployed separately (e.g., on Render, Railway, Fly.io, or similar) and accessible via HTTPS.

## 📁 Project Structure

```
AgriBrain/
├── frontend_streamlit/
│   └── app.py              # Main Streamlit application
├── backend/                # FastAPI backend (separate deployment)
├── ml/                     # ML models and simulation core
├── datasets/               # GeoJSON and training data
├── models/                 # Trained .pkl models
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── .gitignore
└── README.md
```

## 🔧 Configuration

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Edit `.env`:
```env
API_BASE_URL=http://localhost:8000
```

## 📊 API Endpoints Expected

The dashboard expects these FastAPI endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/simulation/ml/simulate` | POST | Run simulation with farm parameters |
| `/api/v1/chat/troubleshoot` | POST | AI chat with simulation context |
| `/api/v1/chat/store-session` | POST | Store simulation context for chat |

### Expected Simulation Response Schema
```json
{
  "recommended_crop": "rice",
  "expected_yield_tons_per_ha": 4.5,
  "roi_percentage": 25.5,
  "risk_level": "Low",
  "shap_values": {"N": 0.15, "P": -0.08, ...},
  "timeline": [...],
  "crop_confidence": 0.87,
  "net_profit_inr": 125000,
  "total_cost_inr": 50000,
  "market_value_inr": 175000,
  "current_growth_phase": "Vegetative",
  "model_version": "1.0.0"
}
```

## 🛠️ Tech Stack

- **Frontend**: Streamlit, Plotly, Pandas
- **Backend**: FastAPI (separate deployment)
- **ML**: scikit-learn, XGBoost, SHAP, Prophet
- **Deployment**: Streamlit Cloud (frontend), Render/Railway (backend)

## 📝 License

MIT License - Feel free to use for educational and research purposes.

---

**Built for Indian Agriculture** 🌾

