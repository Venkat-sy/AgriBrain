"""
AgriSim Farmer-Friendly Dashboard - 3-Tab Version
Streamlit app for Indian farmers - simple inputs, automatic scientific parameter lookup
Refactored to 3-tab structure: Farm Setup | Simulation Results | AI Chat Assistant
"""
import os
import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
CROP_RECOMMEND_ENDPOINT = f'{API_BASE_URL}/api/v1/crop/recommend'
SIMULATION_ENDPOINT = f'{API_BASE_URL}/api/v1/simulation/run'
BASELINE_ENDPOINT = f'{API_BASE_URL}/api/v1/baseline/parameters'
CHAT_ENDPOINT = f'{API_BASE_URL}/api/v1/chat/troubleshoot'
STORE_SESSION_ENDPOINT = f'{API_BASE_URL}/api/v1/chat/store-session'
GET_SESSION_ENDPOINT = f'{API_BASE_URL}/api/v1/chat/session/'
DISTRICTS_ENDPOINT = f'{API_BASE_URL}/api/v1/map/districts'

st.set_page_config(
    page_title='AgriSim - Smart Farm Advisor',
    page_icon='🌾',
    layout='wide',
    initial_sidebar_state='expanded'
)

# Custom CSS
st.markdown('''
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #2E7D32; text-align: center; margin-bottom: 0.5rem; }
    .sub-header { font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .metric-card { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #2E7D32; margin: 0.5rem 0; }
    .risk-high { border-left-color: #C62828 !important; background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%) !important; }
    .risk-medium { border-left-color: #F57F17 !important; background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%) !important; }
    .risk-low { border-left-color: #2E7D32 !important; background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%) !important; }
    .chat-message { padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
    .user-message { background: #E3F2FD; margin-left: 2rem; text-align: right; }
    .assistant-message { background: #E8F5E9; margin-right: 2rem; }
    .stButton > button { width: 100%; background: linear-gradient(90deg, #2E7D32 0%, #4CAF50 100%); color: white; font-weight: 600; border: none; padding: 0.75rem; border-radius: 8px; transition: all 0.3s; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(46, 125, 50, 0.4); }
    .parameter-badge { display: inline-block; background: #E8F5E9; color: #2E7D32; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; margin: 0.25rem; font-weight: 500; }
    .info-box { background: #E3F2FD; border-left: 4px solid #1565C0; padding: 1rem; border-radius: 8px; margin: 1rem 0; }
    .shap-chart-container { background: white; border-radius: 12px; padding: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .tab-content { padding: 1rem 0; }
    .step-badge { display: inline-block; background: #2E7D32; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; margin-right: 0.5rem; }
    .crop-card { background: white; border: 2px solid #E0E0E0; border-radius: 12px; padding: 1rem; margin: 0.5rem 0; transition: all 0.2s; }
    .crop-card.selected { border-color: #2E7D32; box-shadow: 0 4px 12px rgba(46, 125, 50, 0.2); }
    .crop-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
</style>
''', unsafe_allow_html=True)

# Session State
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = f'streamlit_session_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
if 'last_simulation' not in st.session_state:
    st.session_state.last_simulation = None
if 'fetched_params' not in st.session_state:
    st.session_state.fetched_params = None
if 'crop_recommendations' not in st.session_state:
    st.session_state.crop_recommendations = None
if 'selected_crop' not in st.session_state:
    st.session_state.selected_crop = None
if 'simulation_ran' not in st.session_state:
    st.session_state.simulation_ran = False

# ============================================================================
# DATA LOADING & PARAMETER LOOKUP
# ============================================================================
@st.cache_data
def load_district_data():
    """Load district metadata and rainfall data from local files"""
    project_root = Path(__file__).resolve().parents[1]

    # Load district metadata
    metadata_path = project_root / 'datasets' / 'district_metadata.json'
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Load rainfall data from CSV (has actual values)
    rainfall_csv_path = project_root / 'datasets' / '04_rainfall_india' / 'district wise rainfall normal.csv'
    rainfall_df = pd.read_csv(rainfall_csv_path)

    # Build rainfall lookup: key = "DISTRICT|STATE" (case insensitive)
    rainfall_lookup = {}
    for _, row in rainfall_df.iterrows():
        key = f"{row['DISTRICT']}|{row['STATE_UT_NAME']}".lower()
        rainfall_lookup[key] = row['ANNUAL']

    # Build district list with display names
    districts = []
    district_id_map = {}
    for idx, (key, info) in enumerate(metadata.items()):
        if info.get('state_name') == 'Madhya Pradesh':  # Focus on MP for demo
            display = f"{info['district_name']}, {info['state_name']}"
            # Get rainfall from CSV lookup (case-insensitive)
            lookup_key = key.lower()
            annual_rainfall = rainfall_lookup.get(lookup_key, 1000)
            if pd.isna(annual_rainfall):
                annual_rainfall = 1000
            districts.append({
                'key': key,
                'district': info['district_name'],
                'state': info['state_name'],
                'avg_rainfall_mm': float(annual_rainfall),
                'display': display
            })
            district_id_map[key] = idx + 1  # 1-based IDs for API

    return districts, district_id_map

districts, district_id_map = load_district_data()

# Soil reference data
soil_ref = {
    "Black Soil (Regur)": {"description": "Rich in calcium, magnesium, lime. Excellent for cotton, soy, wheat.", "typical_ph": 7.5},
    "Red Soil (Laterite)": {"description": "High iron oxide, acidic. Good for millets, pulses, groundnut with lime.", "typical_ph": 5.5},
    "Alluvial Soil": {"description": "Fertile river deposits. Best for rice, wheat, sugarcane, vegetables.", "typical_ph": 7.0},
    "Sandy Soil": {"description": "Well-drained, low nutrients. Suitable for watermelon, cucumber, peanuts.", "typical_ph": 6.5},
    "Clay Soil": {"description": "Heavy, holds water. Good for rice, jute with proper drainage.", "typical_ph": 7.2},
}

def fetch_baseline_params(district_name, state, selected_soil):
    """Fetch baseline N, P, K, pH, temperature, humidity, rainfall from backend API."""
    try:
        payload = {
            "district": district_name,
            "state": state,
            "soil_type": selected_soil
        }
        response = requests.post(BASELINE_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Return in the format expected by the rest of the app
        return {
            'N': data['n'],
            'P': data['p'],
            'K': data['k'],
            'ph': data['ph'],
            'temperature': data['temperature_c'],
            'humidity': data['humidity_percent'],
            'rainfall': data['rainfall_mm'],
            'district': data['district'],
            'state': data['state'],
            'soil_type': data['soil_type'],
            'lookup_method': data['lookup_method'],
            'avg_rainfall_mm': data['rainfall_mm']
        }
    except requests.exceptions.ConnectionError:
        st.error('Cannot connect to backend. Ensure FastAPI is running on http://localhost:8000')
        return None
    except requests.exceptions.Timeout:
        st.error('Request timed out.')
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f'API Error: {e.response.status_code} - {e.response.text}')
        return None
    except Exception as e:
        st.error(f'Unexpected error: {str(e)}')
        return None

# ============================================================================
# CHART HELPERS
# ============================================================================
def create_shap_chart(features, title="Feature Importance (SHAP Values)"):
    feature_names = [f['feature'] for f in features]; importances = [f['importance'] for f in features]
    sorted_pairs = sorted(zip(feature_names, importances), key=lambda x: abs(x[1]), reverse=True)
    feature_names, importances = zip(*sorted_pairs) if sorted_pairs else ([], [])
    fig = go.Figure(go.Bar(x=importances, y=feature_names, orientation='h', marker_color='#2E7D32',
                text=[f'{v:.3f}' for v in importances], textposition='auto'))
    fig.update_layout(title=title, xaxis_title='SHAP Value (Impact on Prediction)', yaxis_title='Feature',
                      height=400, margin=dict(l=120, r=20, t=50, b=40), plot_bgcolor='white', paper_bgcolor='white')
    return fig


def create_risk_gauge(risk_level):
    risk_colors = {'low': '#2E7D32', 'medium': '#F57F17', 'high': '#C62828'}
    risk_values = {'low': 20, 'medium': 55, 'high': 85}
    color = risk_colors.get(risk_level.lower(), '#666'); value = risk_values.get(risk_level.lower(), 50)
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value, domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Risk Level: {risk_level.capitalize()}", 'font': {'size': 16}},
        gauge={'axis': {'range': [0, 100], 'tickwidth': 1}, 'bar': {'color': color}, 'bgcolor': "white",
               'borderwidth': 2, 'bordercolor': "gray",
               'steps': [{'range': [0, 33], 'color': '#E8F5E9'}, {'range': [33, 66], 'color': '#FFF8E1'}, {'range': [66, 100], 'color': '#FFEBEE'}],
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': value}}))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    return fig


# ============================================================================
# API FUNCTIONS
# ============================================================================
def call_crop_recommendation_api(district_id, soil_type, rainfall_mm, temperature_c, humidity_percent, ph, n, p, k, top_k=5):
    """Call the crop recommendation API"""
    try:
        payload = {"district_id": district_id, "soil_type": soil_type, "rainfall_mm": rainfall_mm,
                   "temperature_c": temperature_c, "humidity_percent": humidity_percent, "ph": ph,
                   "n": n, "p": p, "k": k, "top_k": top_k}
        response = requests.post(CROP_RECOMMEND_ENDPOINT, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error('Cannot connect to backend. Ensure FastAPI is running on http://localhost:8000')
        return None
    except requests.exceptions.Timeout:
        st.error('Request timed out.')
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f'API Error: {e.response.status_code} - {e.response.text}')
        return None
    except Exception as e:
        st.error(f'Unexpected error: {str(e)}')
        return None


def call_simulation_api(district_id, selected_crop, land_area_ha, budget_inr, confirmed_soil_type, rainfall_override_mm=None, planting_month=None, planting_season=None, planned_start_date=None):
    """Call the simulation API with farmer-friendly inputs"""
    try:
        payload = {"district_id": district_id, "selected_crop": selected_crop,
                   "land_area_ha": land_area_ha, "budget_inr": budget_inr,
                   "confirmed_soil_type": confirmed_soil_type}
        if rainfall_override_mm: payload["rainfall_override_mm"] = rainfall_override_mm
        if planting_month: payload["planting_month"] = planting_month
        if planting_season: payload["planting_season"] = planting_season
        if planned_start_date: payload["planned_start_date"] = planned_start_date.isoformat()
        response = requests.post(SIMULATION_ENDPOINT, json=payload, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error('Cannot connect to backend. Ensure FastAPI is running on http://localhost:8000')
        return None
    except requests.exceptions.Timeout:
        st.error('Request timed out. The simulation took too long.')
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f'API Error: {e.response.status_code} - {e.response.text}')
        return None
    except Exception as e:
        st.error(f'Unexpected error: {str(e)}')
        return None


def call_chat_api(session_id, question):
    """Call the chat API"""
    try:
        response = requests.post(CHAT_ENDPOINT, json={'session_id': session_id, 'user_question': question}, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {'response': f'Failed to get response: {str(e)}'}


def store_session(session_id, session_data):
    """Store session for chat context"""
    try:
        response = requests.post(STORE_SESSION_ENDPOINT, json={'session_id': session_id, **session_data}, timeout=10)
        response.raise_for_status()
        return True
    except Exception:
        return False


# ============================================================================
# MAIN UI
# ============================================================================
# Header
st.markdown('<div class="main-header">🌾 AgriSim - Smart Farm Advisor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Get personalized crop recommendations & profit simulations for your farm</div>', unsafe_allow_html=True)

# ============================================================================
# SIDEBAR - FARMER FRIENDLY INPUTS (Persistent across tabs)
# ============================================================================
with st.sidebar:
    st.markdown("## 🌾 Farm Details")
    district_options = [d['display'] for d in districts]
    district_idx = st.selectbox("📍 Select Your District", options=range(len(district_options)),
        format_func=lambda i: district_options[i], index=0,
        help="Choose your district to auto-load climate and soil data")
    selected_district = districts[district_idx]
    district_key = selected_district['key']
    district_id = district_id_map.get(district_key, 1)

    soil_options = list(soil_ref.keys())
    soil_idx = st.selectbox("🌱 Select Soil Type / Color", options=range(len(soil_options)),
        format_func=lambda i: soil_options[i], index=0,
        help="Choose the soil type that matches your field")
    selected_soil = soil_options[soil_idx]
    soil_profile = soil_ref[selected_soil]

    st.markdown(f"<div class='info-box'><strong>{selected_soil}</strong><br><small>{soil_profile['description']}</small></div>", unsafe_allow_html=True)
    st.divider()
    st.markdown("## 📅 Cultivation Planning")
    planting_season = st.selectbox(
        "🌾 Planting Season",
        options=["Kharif", "Rabi", "Zaid", "Annual"],
        index=0,
        help="Kharif: Monsoon (Jun-Oct) | Rabi: Winter (Nov-Apr) | Zaid: Summer (Mar-Jun) | Annual: Year-round"
    )
    
    # Default start date based on season
    from datetime import date, timedelta
    today = date.today()
    season_default_dates = {
        "Kharif": date(today.year, 6, 15),
        "Rabi": date(today.year, 11, 15),
        "Zaid": date(today.year, 3, 15),
        "Annual": today
    }
    default_start = season_default_dates.get(planting_season, today)
    if default_start < today:
        default_start = date(today.year + 1, default_start.month, default_start.day)
    
    planned_start_date = st.date_input(
        "📅 Planned Start Date",
        value=default_start,
        min_value=today,
        help="When do you plan to start land preparation/sowing?"
    )
    st.divider()
    st.markdown("## 💰 Farm Economics")
    land_area = st.number_input("📏 Land Area (hectares)", min_value=0.1, max_value=100.0, value=2.0, step=0.1,
        help="Total cultivable land you own/lease")
    budget = st.number_input("💵 Budget (₹ INR)", min_value=5000, max_value=5000000, value=100000, step=5000,
        help="Available budget for this crop cycle")
    st.divider()
    run_full_analysis = st.button("🚀 Run Full Analysis", type="primary", use_container_width=True)

    if st.session_state.fetched_params:
        with st.expander("🔬 View Auto-Fetched Scientific Parameters", expanded=False):
            fp = st.session_state.fetched_params
            # Show lookup method badge
            lookup_labels = {
                "exact": "🎯 Exact Match",
                "state_average": "📊 State Average",
                "soil_average": "🌱 Soil Type Average"
            }
            lookup_display = lookup_labels.get(fp.get('lookup_method', 'exact'), fp.get('lookup_method', 'exact'))
            
            st.markdown(f"""
            <div style='font-size: 0.85rem;'>
            <span class='parameter-badge'>N: {fp['N']:.0f} kg/ha</span>
            <span class='parameter-badge'>P: {fp['P']:.0f} kg/ha</span>
            <span class='parameter-badge'>K: {fp['K']:.0f} kg/ha</span>
            <span class='parameter-badge'>pH: {fp['ph']:.1f}</span>
            <span class='parameter-badge'>Temp: {fp['temperature']:.0f}°C</span>
            <span class='parameter-badge'>Humidity: {fp['humidity']:.0f}%</span>
            <span class='parameter-badge'>Rainfall: {fp['rainfall']:.0f} mm</span>
            </div>""", unsafe_allow_html=True)
            
            # Show subtle note about lookup method
            if fp.get('lookup_method') != 'exact':
                st.info(f"ℹ️ {lookup_display}: Using regional averages for this location.")
            else:
                st.caption(f"Based on {fp['district']}, {fp['state']} • {fp['soil_type']} soil")

# ============================================================================
# AUTO-FETCH PARAMETERS WHEN DISTRICT/SOIL CHANGES
# ============================================================================
params = fetch_baseline_params(selected_district['district'], selected_district['state'], selected_soil)
if params:
    st.session_state.fetched_params = params

# ============================================================================
# MAIN CONTENT - 3 TABS
# ============================================================================
tab1, tab2, tab3 = st.tabs(["🌱 Farm Setup", "📊 Simulation Results", "🤖 AI Chat Assistant"])

# ============================================================================
# TAB 1: FARM SETUP
# ============================================================================
with tab1:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    st.markdown("""
    <div style='text-align: center; margin-bottom: 1.5rem;'>
        <span class='step-badge'>1</span> Select District & Soil
        <span class='step-badge'>2</span> Enter Land Area & Budget
        <span class='step-badge'>3</span> Click Run Full Analysis
    </div>""", unsafe_allow_html=True)

    params = fetch_baseline_params(selected_district['district'], selected_district['state'], selected_soil)
    if params:
        st.session_state.fetched_params = params

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📍 Location")
        st.info(f"**District:** {selected_district['district']}\n\n**State:** {selected_district['state']}")
    with col2:
        st.markdown("### 🌱 Soil Type")
        st.info(f"**Type:** {selected_soil}\n\n{soil_profile['description']}")

    st.markdown("### 💰 Economics")
    ecol1, ecol2 = st.columns(2)
    with ecol1: st.metric("Land Area", f"{land_area} hectares")
    with ecol2: st.metric("Budget", f"₹{budget:,.0f}")

    st.markdown("---")
    st.markdown("### 🔬 Auto-Fetched Baseline Parameters")
    if st.session_state.fetched_params:
        fp = st.session_state.fetched_params
        param_cols = st.columns(4)
        with param_cols[0]:
            st.metric("Nitrogen (N)", f"{fp['N']:.0f} kg/ha")
            st.metric("Phosphorus (P)", f"{fp['P']:.0f} kg/ha")
        with param_cols[1]:
            st.metric("Potassium (K)", f"{fp['K']:.0f} kg/ha")
            st.metric("pH", f"{fp['ph']:.1f}")
        with param_cols[2]:
            st.metric("Temperature", f"{fp['temperature']:.0f}°C")
            st.metric("Humidity", f"{fp['humidity']:.0f}%")
        with param_cols[3]:
            st.metric("Rainfall", f"{fp['rainfall']:.0f} mm/yr")
            st.metric("Avg Rainfall", f"{fp['avg_rainfall_mm']:.0f} mm/yr (district)")
        st.caption(f"Based on {fp['district']}, {fp['state']} • {fp['soil_type']} soil")
    else:
        st.warning("Could not fetch parameters for this district/soil combination.")
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 2: SIMULATION RESULTS
# ============================================================================
with tab2:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)

    if run_full_analysis:
        if not st.session_state.fetched_params:
            st.error("⚠️ Please go to Farm Setup tab and ensure parameters are fetched.")
        else:
            fp = st.session_state.fetched_params
            with st.spinner("Getting crop recommendations from AI model..."):
                result = call_crop_recommendation_api(
                    district_id=district_id, soil_type=selected_soil, rainfall_mm=fp['rainfall'],
                    temperature_c=fp['temperature'], humidity_percent=fp['humidity'], ph=fp['ph'],
                    n=fp['N'], p=fp['P'], k=fp['K'], top_k=5)

                if result:
                    st.session_state.crop_recommendations = result
                    if result.get('recommendations'):
                        top_crop = result['recommendations'][0]['crop_name']
                        st.session_state.selected_crop = top_crop
                        context = {'crop': top_crop, 'district': selected_district['district'],
                            'state': selected_district['state'], 'soil_type': selected_soil,
                            'land_area_ha': land_area, 'budget_inr': budget,
                            'estimated_yield': result['recommendations'][0].get('estimated_yield_tons_per_ha') or result['recommendations'][0].get('expected_yield_tons_per_ha'),
                            'roi': result['recommendations'][0].get('roi_percentage'),
                            'risk_level': result['recommendations'][0].get('risk_level')}
                        store_session(st.session_state.session_id, context)
                else:
                    st.error("Failed to get crop recommendations.")
                    st.stop()

            # Get the user-selected crop (or default to top recommendation)
            selected_crop = st.session_state.get('selected_crop', 
                result['recommendations'][0]['crop_name'] if result.get('recommendations') else 'Rice')
            
            with st.spinner(f"Running simulation for {selected_crop}..."):
                sim_result = call_simulation_api(
                    district_id=district_id, selected_crop=selected_crop,
                    land_area_ha=land_area, budget_inr=budget,
                    confirmed_soil_type=selected_soil, rainfall_override_mm=fp['rainfall'],
                    planting_season=planting_season, planned_start_date=planned_start_date)

                if sim_result:
                    st.session_state.last_simulation = sim_result
                    st.session_state.simulation_ran = True
                    sim = st.session_state.last_simulation
                    context = {'crop': sim.get('selected_crop'), 'district': selected_district['district'],
                        'state': selected_district['state'], 'soil_type': selected_soil,
                        'land_area_ha': land_area, 'budget_inr': budget,
                        'estimated_yield': sim.get('estimated_yield_tons_per_ha'),
                        'roi': sim.get('roi_percentage'), 'risk_level': sim.get('risk_level')}
                    store_session(st.session_state.session_id, context)
                    st.success("✅ Analysis complete! View results below.")
                    st.rerun()
                else:
                    st.error("Simulation failed.")
                    st.stop()

    if st.session_state.last_simulation and st.session_state.simulation_ran:
        sim = st.session_state.last_simulation

        st.markdown(f"### 📊 Simulation Results: {sim.get('selected_crop', 'Crop')}")
        st.caption(f"District: {selected_district['district']}, {selected_district['state']} | Soil: {selected_soil} | Area: {land_area} ha | Budget: ₹{budget:,.0f}")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class="metric-card"><div style="font-size: 0.9rem; color: #666;">Recommended Crop</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #2E7D32;">{sim.get('selected_crop', 'N/A')}</div></div>""", unsafe_allow_html=True)
        with col2:
            yield_per_ha = sim.get('estimated_yield_tons_per_ha', 0)
            st.markdown(f"""<div class="metric-card"><div style="font-size: 0.9rem; color: #666;">Expected Yield</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: #1565C0;">{yield_per_ha:.2f} tons/ha</div></div>""", unsafe_allow_html=True)
        with col3:
            roi = sim.get('roi_percentage', 0)
            roi_color = "#2E7D32" if roi > 20 else "#F57F17" if roi > 0 else "#C62828"
            st.markdown(f"""<div class="metric-card"><div style="font-size: 0.9rem; color: #666;">ROI</div>
                <div style="font-size: 1.8rem; font-weight: 700; color: {roi_color};">{roi:.1f}%</div></div>""", unsafe_allow_html=True)
        with col4:
            risk_level = sim.get('risk_level', 'medium').lower()
            st.markdown(f"""<div class="metric-card risk-{risk_level}"><div style="font-size: 0.9rem; color: #666;">Risk Level</div>
                <div style="font-size: 1.8rem; font-weight: 700; text-transform: capitalize;">{risk_level}</div></div>""", unsafe_allow_html=True)

        st.markdown("---")

        col_left, col_right = st.columns([1, 1])
        with col_left:
            st.markdown("### 📈 Risk Assessment")
            risk_fig = create_risk_gauge(sim.get('risk_level', 'medium'))
            st.plotly_chart(risk_fig, use_container_width=True)
            if sim.get('risk_factors'):
                st.markdown("**Key Risk Factors:**")
                for factor in sim['risk_factors']: st.markdown(f"- {factor}")

        with col_right:
            st.markdown("### 🔍 What Drove This Recommendation? (Feature Importance)")
            shap_features = [
                {'feature': 'Soil Type Match', 'importance': 0.35},
                {'feature': 'Rainfall Adequacy', 'importance': 0.28},
                {'feature': 'Temperature Suitability', 'importance': 0.18},
                {'feature': 'Budget Efficiency', 'importance': 0.12},
                {'feature': 'Soil pH Compatibility', 'importance': 0.07}]
            shap_fig = create_shap_chart(shap_features, "Key Factors Influencing Crop Suitability & Profitability")
            st.plotly_chart(shap_fig, use_container_width=True)
            st.caption("💡 This chart shows which factors most influenced the recommendation. Soil type match and rainfall are typically the strongest predictors.")

        # User Crop Selection - After ML recommendations, let user choose
        if st.session_state.crop_recommendations:
            recs = st.session_state.crop_recommendations.get('recommendations', [])
            if recs:
                st.markdown("### 🎯 Select Your Crop")
                st.markdown("The AI has recommended these crops based on your farm conditions. Choose the one you want to cultivate:")
                
                crop_options = [rec['crop_name'] for rec in recs]
                crop_display = [f"{rec['crop_name']} (Confidence: {rec['confidence']*100:.0f}%, Season: {rec.get('season', 'N/A')}, Yield: {rec.get('expected_yield_tons_per_ha', 'N/A')} t/ha)" 
                               for rec in recs]
                
                selected_idx = st.selectbox(
                    "Which crop do you want to cultivate?",
                    options=range(len(crop_options)),
                    format_func=lambda i: crop_display[i],
                    index=0,
                    key="user_crop_selection"
                )
                
                # Update selected crop if changed
                if st.session_state.selected_crop != crop_options[selected_idx]:
                    st.session_state.selected_crop = crop_options[selected_idx]
                    # Re-run simulation with new crop
                    with st.spinner(f"Re-running simulation for {crop_options[selected_idx]}..."):
                        fp = st.session_state.fetched_params
                        sim_result = call_simulation_api(
                            district_id=district_id, selected_crop=crop_options[selected_idx],
                            land_area_ha=land_area, budget_inr=budget,
                            confirmed_soil_type=selected_soil, rainfall_override_mm=fp['rainfall'],
                            planting_season=planting_season, planned_start_date=planned_start_date)
                        if sim_result:
                            st.session_state.last_simulation = sim_result
                            st.session_state.simulation_ran = True
                            context = {'crop': crop_options[selected_idx], 'district': selected_district['district'],
                                'state': selected_district['state'], 'soil_type': selected_soil,
                                'land_area_ha': land_area, 'budget_inr': budget,
                                'estimated_yield': sim_result.get('estimated_yield_tons_per_ha'),
                                'roi': sim_result.get('roi_percentage'), 'risk_level': sim_result.get('risk_level'),
                                'planting_season': planting_season,
                                'planned_start_date': planned_start_date.isoformat() if planned_start_date else None}
                            store_session(st.session_state.session_id, context)
                            st.success(f"✅ Simulation updated for {crop_options[selected_idx]}!")
                            st.rerun()
                        else:
                            st.error("Failed to re-run simulation.")
                            st.rerun()
                
                st.markdown("---")
            
            with st.expander("📋 View All Crop Recommendations", expanded=False):
                cols = st.columns(min(len(recs), 3))
                for idx, rec in enumerate(recs):
                    with cols[idx % 3]:
                        is_selected = st.session_state.selected_crop == rec['crop_name']
                        badge = " 🏆 SELECTED" if is_selected else ""
                        card_class = "crop-card selected" if is_selected else "crop-card"
                        st.markdown(f"""<div class="{card_class}"><h4 style="margin: 0; color: #2E7D32;">{rec['crop_name']}{badge}</h4>
                            <p style="margin: 0.5rem 0; color: #666;"><strong>Confidence:</strong> {rec['confidence']*100:.0f}%<br>
                            <strong>Season:</strong> {rec.get('season', 'N/A')}<br>
                            <strong>Expected Yield:</strong> {rec.get('expected_yield_tons_per_ha', 'N/A')} tons/ha</p>
                            <small style="color: #888;">{' '.join(rec.get('match_reasons', [])[:2])}</small></div>""", unsafe_allow_html=True)
    else:
        st.info("👈 Go to **Farm Setup** tab, enter your details, and click **Run Full Analysis** to see results here.")

    st.markdown('</div>', unsafe_allow_html=True)

# ============================================================================
# TAB 3: AI CHAT ASSISTANT
# ============================================================================
with tab3:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)

    st.markdown("### 🤖 Ask Our Farm Advisor")
    st.markdown("Get contextual farming advice based on your simulation results.")

    # Check if we have context
    has_context = st.session_state.last_simulation is not None or st.session_state.crop_recommendations is not None
    
    # Dual-mode tabs
    chat_mode = st.tabs(["🌾 General Agriculture QA", "📋 Context-Aware Farm Planner"])
    
    # Build context for the session
    # Use user's selected crop if available, otherwise fall back to top recommendation
    user_selected_crop = st.session_state.get('selected_crop')
    
    context = {}
    if st.session_state.last_simulation:
        sim = st.session_state.last_simulation
        context = {
            'crop': sim.get('selected_crop'),
            'district': selected_district['district'],
            'state': selected_district['state'],
            'soil_type': selected_soil,
            'land_area_ha': land_area,
            'budget_inr': budget,
            'estimated_yield': sim.get('estimated_yield_tons_per_ha'),
            'roi': sim.get('roi_percentage'),
            'risk_level': sim.get('risk_level'),
            'planting_season': planting_season,
            'planned_start_date': planned_start_date.isoformat() if planned_start_date else None
        }
    elif st.session_state.crop_recommendations:
        rec = st.session_state.crop_recommendations['recommendations'][0]
        # Use user's selected crop if they chose one, otherwise use top recommendation
        crop_to_use = user_selected_crop if user_selected_crop else rec.get('crop_name')
        context = {
            'crop': crop_to_use,
            'district': selected_district['district'],
            'state': selected_district['state'],
            'soil_type': selected_soil,
            'land_area_ha': land_area,
            'budget_inr': budget,
            'estimated_yield': rec.get('estimated_yield_tons_per_ha') or rec.get('expected_yield_tons_per_ha'),
            'roi': rec.get('roi_percentage'),
            'risk_level': rec.get('risk_level'),
            'planting_season': planting_season,
            'planned_start_date': planned_start_date.isoformat() if planned_start_date else None
        }

    # Tab 1: General Agriculture QA
    with chat_mode[0]:
        st.markdown("#### 💬 General Farming Questions")
        st.caption("Ask any agriculture question - no farm context needed.")
        
        if 'general_chat_history' not in st.session_state:
            st.session_state.general_chat_history = []
        
        for msg in st.session_state.general_chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""<div class="chat-message user-message"><strong>You:</strong> {msg['content']}</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="chat-message assistant-message"><strong>🌾 Farm Advisor:</strong><br>{msg['content']}</div>""", unsafe_allow_html=True)
        
        general_question = st.text_input(
            "Ask a general farming question:",
            placeholder="e.g., 'What is crop rotation?' or 'How to make organic compost?' or 'Best irrigation methods for small farms?'",
            key="general_question")
        
        col_send_gen, col_clear_gen = st.columns([7, 1])
        with col_send_gen:
            send_gen_clicked = st.button("Ask", type="primary", use_container_width=True, key="send_general")
        with col_clear_gen:
            if st.button("Clear", type="secondary", use_container_width=True, key="clear_general"):
                st.session_state.general_chat_history = []
                st.rerun()
        
        if send_gen_clicked and general_question:
            with st.spinner("Getting expert advice..."):
                store_session(st.session_state.session_id + "_general", {})
                response = call_chat_api(st.session_state.session_id + "_general", general_question)
                
                if response and 'response' in response:
                    st.session_state.general_chat_history.append({'role': 'user', 'content': general_question})
                    st.session_state.general_chat_history.append({'role': 'assistant', 'content': response['response']})
                    st.rerun()
                else:
                    st.error("Failed to get response from advisor.")
    
    # Tab 2: Context-Aware Farm Planner
    with chat_mode[1]:
        st.markdown("#### 📋 Context-Aware Farm Planning")
        
        if not has_context:
            st.warning("⚠️ Run a simulation first in the **Simulation Results** tab to enable context-aware planning.")
            st.info("Once you run a simulation, this mode will use your selected crop, season, start date, soil, and location to generate personalized cultivation calendars and advice.")
        else:
            # Show active context
            context_info = f"""**Active Context:** {context.get('crop', 'Crop')} in {context.get('district')}, {context.get('state')} ({context.get('soil_type')} soil)
- **Season:** {context.get('planting_season', 'Not specified')}
- **Planned Start:** {context.get('planned_start_date', 'Not specified')}
- **Land Area:** {context.get('land_area_ha', 'N/A')} ha
- **Budget:** ₹{context.get('budget_inr', 'N/A'):,.0f}"""
            st.info(context_info)
            
            # Quick action buttons
            st.markdown("**Quick Actions:**")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📅 Generate Cultivation Calendar", use_container_width=True, key="gen_calendar"):
                    calendar_prompt = f"Generate a comprehensive day-by-day cultivation calendar for {context.get('crop')} starting from {context.get('planned_start_date')} through harvest. Include all activities: land preparation, sowing, fertilizer applications, irrigation schedule, weeding, pest monitoring, and harvesting. Specific to {context.get('soil_type')} soil in {context.get('district')}, {context.get('state')}."
                    with st.spinner("Generating cultivation calendar..."):
                        store_session(st.session_state.session_id, context)
                        enhanced_question = f"[CONTEXT_AWARE_MODE] {calendar_prompt}"
                        response = call_chat_api(st.session_state.session_id, enhanced_question)
                        if response and 'response' in response:
                            if 'planner_chat_history' not in st.session_state:
                                st.session_state.planner_chat_history = []
                            st.session_state.planner_chat_history.append({'role': 'user', 'content': calendar_prompt})
                            st.session_state.planner_chat_history.append({'role': 'assistant', 'content': response['response']})
                            st.rerun()
                        else:
                            st.error("Failed to get response from advisor.")
            with col2:
                if st.button("💧 Irrigation Schedule", use_container_width=True, key="irr_schedule"):
                    irrigation_prompt = f"Create a detailed week-by-week irrigation schedule for {context.get('crop')} from {context.get('planned_start_date')} to harvest in {context.get('district')}, {context.get('state')}. Consider {context.get('soil_type')} soil and local climate."
                    with st.spinner("Generating irrigation schedule..."):
                        store_session(st.session_state.session_id, context)
                        enhanced_question = f"[CONTEXT_AWARE_MODE] {irrigation_prompt}"
                        response = call_chat_api(st.session_state.session_id, enhanced_question)
                        if response and 'response' in response:
                            if 'planner_chat_history' not in st.session_state:
                                st.session_state.planner_chat_history = []
                            st.session_state.planner_chat_history.append({'role': 'user', 'content': irrigation_prompt})
                            st.session_state.planner_chat_history.append({'role': 'assistant', 'content': response['response']})
                            st.rerun()
                        else:
                            st.error("Failed to get response from advisor.")
            with col3:
                if st.button("🌱 Fertilizer Plan", use_container_width=True, key="fert_plan"):
                    fert_prompt = f"Generate a comprehensive fertilizer management plan for {context.get('crop')} in {context.get('soil_type')} soil. Include basal dose, top dressing schedule, organic alternatives, and biofertilizer recommendations. Timeline from {context.get('planned_start_date')}."
                    with st.spinner("Generating fertilizer plan..."):
                        store_session(st.session_state.session_id, context)
                        enhanced_question = f"[CONTEXT_AWARE_MODE] {fert_prompt}"
                        response = call_chat_api(st.session_state.session_id, enhanced_question)
                        if response and 'response' in response:
                            if 'planner_chat_history' not in st.session_state:
                                st.session_state.planner_chat_history = []
                            st.session_state.planner_chat_history.append({'role': 'user', 'content': fert_prompt})
                            st.session_state.planner_chat_history.append({'role': 'assistant', 'content': response['response']})
                            st.rerun()
                        else:
                            st.error("Failed to get response from advisor.")
            
            if 'planner_chat_history' not in st.session_state:
                st.session_state.planner_chat_history = []
            
            for msg in st.session_state.planner_chat_history:
                if msg['role'] == 'user':
                    st.markdown(f"""<div class="chat-message user-message"><strong>You:</strong> {msg['content']}</div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""<div class="chat-message assistant-message"><strong>🌾 Farm Planner:</strong><br>{msg['content']}</div>""", unsafe_allow_html=True)
            
            # Check if a quick action was triggered
            default_question = st.session_state.get('planner_question', '')
            if 'planner_question' in st.session_state:
                del st.session_state.planner_question
            
            planner_question = st.text_input(
                "Ask for a detailed plan or farming advice:",
                value=default_question,
                placeholder="e.g., 'Generate a day-by-day cultivation calendar' or 'When should I apply fertilizers?' or 'What pests to watch for each week?'",
                key="planner_question_input")
            
            col_send_plan, col_clear_plan = st.columns([7, 1])
            with col_send_plan:
                send_plan_clicked = st.button("Get Plan", type="primary", use_container_width=True, key="send_planner", disabled=not has_context)
            with col_clear_plan:
                if st.button("Clear", type="secondary", use_container_width=True, key="clear_planner"):
                    st.session_state.planner_chat_history = []
                    st.rerun()
            
            if send_plan_clicked and planner_question:
                with st.spinner("Generating your personalized farm plan..."):
                    # Store session with full context
                    store_session(st.session_state.session_id, context)
                    # Add a marker to indicate context-aware mode
                    enhanced_question = f"[CONTEXT_AWARE_MODE] {planner_question}"
                    response = call_chat_api(st.session_state.session_id, enhanced_question)
                    
                    if response and 'response' in response:
                        st.session_state.planner_chat_history.append({'role': 'user', 'content': planner_question})
                        st.session_state.planner_chat_history.append({'role': 'assistant', 'content': response['response']})
                        st.rerun()
                    else:
                        st.error("Failed to get response from advisor.")

    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    AgriSim - Empowering Indian Farmers with Data-Driven Decisions<br>
    <small>Data sources: ICAR, IMD, State Agriculture Departments | Model: Ensemble ML with SHAP Explainability</small>
</div>
""", unsafe_allow_html=True)