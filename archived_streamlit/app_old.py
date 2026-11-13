"""
AgriSim ML Validation Dashboard
Streamlit app for testing ML models, simulation engine, and SHAP explainability
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
SIMULATE_ENDPOINT = f'{API_BASE_URL}/api/v1/simulation/ml/simulate'
CHAT_ENDPOINT = f'{API_BASE_URL}/api/v1/chat/troubleshoot'
STORE_SESSION_ENDPOINT = f'{API_BASE_URL}/api/v1/chat/store-session'
GET_SESSION_ENDPOINT = f'{API_BASE_URL}/api/v1/chat/session/'

st.set_page_config(
    page_title='AgriSim ML Validation Dashboard',
    page_icon='🌾',
    layout='wide',
    initial_sidebar_state='expanded'
)

st.markdown('''
<style>
    .main-header { font-size: 2.5rem; font-weight: 700; color: #2E7D32; text-align: center; margin-bottom: 1rem; }
    .metric-card { background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%); padding: 1.5rem; border-radius: 12px; border-left: 4px solid #2E7D32; margin: 0.5rem 0; }
    .risk-high { border-left-color: #C62828 !important; background: linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%) !important; }
    .risk-medium { border-left-color: #F57F17 !important; background: linear-gradient(135deg, #FFF8E1 0%, #FFECB3 100%) !important; }
    .risk-low { border-left-color: #2E7D32 !important; background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%) !important; }
    .chat-message { padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
    .user-message { background: #E3F2FD; margin-left: 2rem; text-align: right; }
    .assistant-message { background: #E8F5E9; margin-right: 2rem; }
    .stButton > button { width: 100%; background: linear-gradient(90deg, #2E7D32 0%, #4CAF50 100%); color: white; font-weight: 600; border: none; padding: 0.75rem; border-radius: 8px; transition: all 0.3s; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(46, 125, 50, 0.4); }
</style>
''', unsafe_allow_html=True)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = f'streamlit_session_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
if 'last_simulation' not in st.session_state:
    st.session_state.last_simulation = None
# AgriSim ML Validation Dashboard - placeholder
def call_simulate_api(params):
    try:
        response = requests.post(SIMULATE_ENDPOINT, json=params, timeout=30)
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

def call_chat_api(session_id, question):
    try:
        response = requests.post(CHAT_ENDPOINT, json={'session_id': session_id, 'user_question': question}, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        st.error('Cannot connect to backend chat endpoint.')
        return None
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        st.error(f'Chat API Error: {e.response.status_code} - {e.response.text}')
        return None
    except Exception as e:
        st.error(f'Chat error: {str(e)}')
        return None

def store_session(session_id, simulation_data):
    try:
        response = requests.post(f'{STORE_SESSION_ENDPOINT}?session_id={session_id}', json=simulation_data, timeout=10)
        return response.status_code == 200
    except Exception:
        return False

def create_shap_chart(shap_values):
    if not shap_values:
        return None
    sorted_items = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
    features = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    colors = ['#C62828' if v < 0 else '#2E7D32' for v in values]
    fig = go.Figure(data=[go.Bar(x=values, y=features, orientation='h', marker_color=colors, text=[f'{v:+.3f}' for v in values], textposition='outside', hovertemplate='<b>%{y}</b><br>SHAP Value: %{x:+.3f}<extra></extra>')])
    fig.update_layout(title={'text': 'SHAP Feature Impact Scores', 'font': {'size': 16, 'color': '#2E7D32'}, 'x': 0.5}, xaxis_title='SHAP Value (Impact on Model Output)', yaxis_title='Feature', height=400 + len(features) * 25, margin=dict(l=150, r=50, t=60, b=50), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family='Inter, sans-serif', size=12))
    fig.update_xaxes(zeroline=True, zerolinewidth=2, zerolinecolor='#9E9E9E')
    return fig

def create_yield_gauge(yield_tons_per_ha, crop):
    max_yields = {'rice': 8, 'wheat': 6, 'maize': 10, 'cotton': 4, 'sugarcane': 100}
    max_yield = max_yields.get(crop.lower(), 10)
    fig = go.Figure(go.Indicator(mode='gauge+number+delta', value=yield_tons_per_ha, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': f'{crop.capitalize()} Yield (tons/ha)', 'font': {'size': 16}}, delta={'reference': max_yield * 0.7, 'increasing': {'color': '#2E7D32'}}, gauge={'axis': {'range': [None, max_yield], 'tickwidth': 1, 'tickcolor': 'darkgreen'}, 'bar': {'color': '#2E7D32'}, 'bgcolor': 'white', 'borderwidth': 2, 'bordercolor': 'gray', 'steps': [{'range': [0, max_yield * 0.4], 'color': '#FFEBEE'}, {'range': [max_yield * 0.4, max_yield * 0.7], 'color': '#FFF8E1'}, {'range': [max_yield * 0.7, max_yield], 'color': '#E8F5E9'}], 'threshold': {'line': {'color': 'red', 'width': 4}, 'thickness': 0.75, 'value': max_yield * 0.9}}))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig

def create_roi_gauge(roi):
    fig = go.Figure(go.Indicator(mode='gauge+number', value=roi, domain={'x': [0, 1], 'y': [0, 1]}, title={'text': 'ROI (%)', 'font': {'size': 16}}, gauge={'axis': {'range': [-50, 200], 'tickwidth': 1, 'tickcolor': 'darkgreen'}, 'bar': {'color': '#1565C0' if roi >= 0 else '#C62828'}, 'bgcolor': 'white', 'borderwidth': 2, 'bordercolor': 'gray', 'steps': [{'range': [-50, 0], 'color': '#FFEBEE'}, {'range': [0, 20], 'color': '#FFF8E1'}, {'range': [20, 50], 'color': '#E8F5E9'}, {'range': [50, 200], 'color': '#C8E6C9'}]}))
    fig.update_layout(height=250, margin=dict(l=20, r=20, t=40, b=20))
    return fig
# SIDEBAR
st.sidebar.markdown("<h2 style='color: #2E7D32;'>Simulation Parameters</h2>", unsafe_allow_html=True)
st.sidebar.markdown('### Soil Nutrients (kg/ha)')
n = st.sidebar.slider('Nitrogen (N)', 0, 200, 80, help='Nitrogen content in soil')
p = st.sidebar.slider('Phosphorus (P)', 0, 100, 40, help='Phosphorus content in soil')
k = st.sidebar.slider('Potassium (K)', 0, 150, 50, help='Potassium content in soil')

st.sidebar.markdown('### Environmental Conditions')
ph = st.sidebar.slider('Soil pH', 4.0, 9.0, 6.5, 0.1, help='Soil acidity/alkalinity')
temperature = st.sidebar.slider('Temperature (C)', 10.0, 45.0, 27.0, 0.5, help='Average temperature')
humidity = st.sidebar.slider('Humidity (%)', 20.0, 100.0, 70.0, 1.0, help='Relative humidity')
rainfall = st.sidebar.slider('Rainfall (mm)', 0, 3000, 800, 50, help='Annual rainfall')

st.sidebar.markdown('### Farm Economics')
land_area = st.sidebar.slider('Land Area (hectares)', 0.1, 50.0, 2.0, 0.1, help='Total cultivable land')
budget = st.sidebar.slider('Budget (INR)', 10000, 500000, 100000, 5000, help='Available budget for cultivation')

st.sidebar.markdown('### Location (Optional)')
district = st.sidebar.text_input('District', placeholder='e.g., East Godavari')
state = st.sidebar.text_input('State', placeholder='e.g., Andhra Pradesh')

run_simulation = st.sidebar.button('Run Simulation', type='primary', use_container_width=True)

# MAIN DASHBOARD
st.markdown("<h1 class='main-header'>AgriSim ML Validation Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1.1rem;'>Test ML models, simulation engine, and SHAP explainability</p>", unsafe_allow_html=True)

tab1, tab2 = st.tabs(['Simulation Results', 'AI Chat Assistant'])

with tab1:
    if run_simulation:
        with st.spinner('Running simulation...'):
            request_params = {'N': float(n), 'P': float(p), 'K': float(k), 'temperature': float(temperature), 'humidity': float(humidity), 'ph': float(ph), 'rainfall': float(rainfall), 'land_area': float(land_area), 'budget': float(budget)}
            if district:
                request_params['district'] = district
            if state:
                request_params['state'] = state
            result = call_simulate_api(request_params)
            if result:
                st.session_state.last_simulation = result
                session_data = {'selected_crop': result.get('recommended_crop', ''), 'budget_inr': budget, 'current_growth_phase': result.get('current_growth_phase', ''), 'district_name': district, 'soil_type': 'loam', 'land_area_ha': land_area, 'estimated_yield_tons_per_ha': result.get('expected_yield_tons_per_ha', 0), 'irrigation_demand_mm': rainfall * 0.5, 'crop_failure_risk': result.get('risk_level', 'Low'), 'total_cost_inr': result.get('total_cost_inr', 0), 'net_profit_inr': result.get('net_profit_inr', 0), 'risk_level': result.get('risk_level', 'Low'), 'risk_factors': result.get('risk_factors', []), 'cost_breakdown': [], 'timeline': result.get('timeline', []), 'model_version': result.get('model_version', '1.0.0'), 'generated_at': datetime.utcnow().isoformat()}
                store_session(st.session_state.session_id, session_data)
    if st.session_state.last_simulation:
        result = st.session_state.last_simulation
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""<div class='metric-card risk-{result.get('risk_level', 'low').lower()}'><h4 style='margin: 0; color: #2E7D32;'>Recommended Crop</h4><h2 style='margin: 0.5rem 0;'>{result.get('recommended_crop', 'N/A').capitalize()}</h2><p style='margin: 0; color: #666;'>Confidence: {result.get('crop_confidence', 0):.1%}</p></div>""", unsafe_allow_html=True)
        with col2:
            yield_val = result.get('expected_yield_tons_per_ha', 0)
            st.markdown(f"""<div class='metric-card'><h4 style='margin: 0; color: #2E7D32;'>Expected Yield</h4><h2 style='margin: 0.5rem 0;'>{yield_val:.2f} tons/ha</h2><p style='margin: 0; color: #666;'>Total: {result.get('expected_yield_tons', 0):.2f} tons</p></div>""", unsafe_allow_html=True)
        with col3:
            roi = result.get('roi_percentage', 0)
            roi_class = 'risk-high' if roi < 0 else 'risk-low' if roi > 20 else 'risk-medium'
            st.markdown(f"""<div class='metric-card {roi_class}'><h4 style='margin: 0; color: #2E7D32;'>ROI</h4><h2 style='margin: 0.5rem 0;'>{roi:.1f}%</h2><p style='margin: 0; color: #666;'>Profit: {result.get('net_profit_inr', 0):,.0f}</p></div>""", unsafe_allow_html=True)
        with col4:
            risk_level = result.get('risk_level', 'Low')
            risk_class = f'risk-{risk_level.lower()}'
            risk_emoji = {'High': 'Red', 'Medium': 'Yellow', 'Low': 'Green'}.get(risk_level, 'Gray')
            st.markdown(f"""<div class='metric-card {risk_class}'><h4 style='margin: 0; color: #2E7D32;'>Risk Level</h4><h2 style='margin: 0.5rem 0;'>{risk_emoji} {risk_level}</h2><p style='margin: 0; color: #666;'>{len(result.get('risk_factors', []))} risk factors</p></div>""", unsafe_allow_html=True)
        
        st.divider()
        chart_col1, chart_col2, chart_col3 = st.columns(3)
        with chart_col1:
            fig_yield = create_yield_gauge(result.get('expected_yield_tons_per_ha', 0), result.get('recommended_crop', 'rice'))
            st.plotly_chart(fig_yield, use_container_width=True)
        with chart_col2:
            fig_roi = create_roi_gauge(result.get('roi_percentage', 0))
            st.plotly_chart(fig_roi, use_container_width=True)
        with chart_col3:
            risk_factors = result.get('risk_factors', [])
            if risk_factors:
                fig_risk = go.Figure(go.Bar(x=[1] * len(risk_factors), y=risk_factors, orientation='h', marker_color='#C62828', text=risk_factors, textposition='inside', hovertemplate='<b>%{y}</b><extra></extra>'))
                fig_risk.update_layout(title={'text': 'Risk Factors', 'font': {'size': 14}, 'x': 0.5}, xaxis={'visible': False}, yaxis={'visible': False}, height=250, margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_risk, use_container_width=True)
            else:
                st.success('No significant risk factors identified')
        st.divider()
        st.markdown('### Financial Breakdown')
        fin_col1, fin_col2, fin_col3 = st.columns(3)
        with fin_col1:
            st.metric('Total Cost', f"{result.get('total_cost_inr', 0):,.0f}")
        with fin_col2:
            st.metric('Market Value', f"{result.get('market_value_inr', 0):,.0f}")
        with fin_col3:
            st.metric('Net Profit', f"{result.get('net_profit_inr', 0):,.0f}")
        
        st.divider()
        st.markdown('### SHAP Feature Impact Analysis')
        shap_values = result.get('shap_values', {})
        if shap_values:
            fig_shap = create_shap_chart(shap_values)
            if fig_shap:
                st.plotly_chart(fig_shap, use_container_width=True)
            with st.expander('View SHAP Values as Table'):
                shap_df = pd.DataFrame(sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True), columns=['Feature', 'SHAP Value'])
                shap_df['Impact'] = shap_df['SHAP Value'].apply(lambda x: 'Positive' if x > 0 else 'Negative')
                st.dataframe(shap_df, use_container_width=True, hide_index=True)
        else:
            st.info('SHAP values not available for this simulation')
        
        st.divider()
        timeline = result.get('timeline', [])
        if timeline:
            st.markdown('### Crop Growth Timeline')
            for phase in timeline:
                st.markdown(f"""<div style='background: #F1F8E9; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 3px solid #2E7D32;'><strong>{phase.get('phase', 'Phase')}</strong> (Day {phase.get('days_after_sowing', 0)})<ul style='margin: 0.5rem 0; padding-left: 1.5rem;'>{''.join(f"<li>{act}</li>" for act in phase.get('activities', []))}</ul></div>""", unsafe_allow_html=True)
        
        with st.expander('Raw API Response (Debug)'):
            st.json(result)
    else:
        st.markdown("""<div style='text-align: center; padding: 3rem; color: #666;'><h3>Configure parameters in the sidebar and click 'Run Simulation'</h3><p>This dashboard tests the AgriSim ML pipeline:</p><ul style='display: inline-block; text-align: left;'><li>Crop Recommendation Model</li><li>Yield Prediction Model</li><li>SHAP Explainability</li><li>Risk Assessment</li><li>Financial Projections</li></ul></div>""", unsafe_allow_html=True)

with tab2:
    st.markdown('### AI Digital Twin Assistant')
    st.markdown('Ask questions about your simulated farm. The assistant uses your simulation context.')
    
    if not st.session_state.last_simulation:
        st.warning('Run a simulation first to enable context-aware chat.')
    else:
        result = st.session_state.last_simulation
        st.success(f"Active context: **{result.get('recommended_crop', '').capitalize()}** in **{result.get('current_growth_phase', 'Growth')}** phase")
    
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg['role'] == 'user':
                st.markdown(f"""<div class='chat-message user-message'><strong>You:</strong> {msg['content']}</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class='chat-message assistant-message'><strong>AgriSim AI:</strong><br>{msg['content']}</div>""", unsafe_allow_html=True)
    
    with st.form('chat_form', clear_on_submit=True):
        user_question = st.text_input('Your question:', placeholder='e.g., How should I irrigate during this phase? What pests to watch for?', key='chat_input')
        submitted = st.form_submit_button('Send', use_container_width=True)
        
        if submitted and user_question:
            st.session_state.chat_history.append({'role': 'user', 'content': user_question})
            with st.spinner('Thinking...'):
                chat_result = call_chat_api(st.session_state.session_id, user_question)
                if chat_result:
                    ai_response = chat_result.get('response', 'No response received')
                else:
                    ai_response = 'Failed to get response. Ensure the backend is running and a simulation session exists.'
            st.session_state.chat_history.append({'role': 'assistant', 'content': ai_response})
            st.rerun()

st.markdown('---')
st.markdown("<p style='text-align: center; color: #999;'>AgriSim ML Validation Dashboard | Built with Streamlit, FastAPI, and for Indian Agriculture</p>", unsafe_allow_html=True)
