from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime, date, timedelta
import json

from backend.core.redis_client import get_session as redis_get_session, save_session as redis_save_session, delete_session as redis_delete_session

router = APIRouter(prefix='/api/v1/chat', tags=['chat'])


class ChatRequest(BaseModel):
    session_id: str
    user_question: str


class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime

    model_config = ConfigDict(protected_namespaces=())


class StoreSessionRequest(BaseModel):
    session_id: str
    crop: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    soil_type: Optional[str] = None
    land_area_ha: Optional[float] = None
    budget_inr: Optional[float] = None
    estimated_yield: Optional[float] = None
    roi: Optional[float] = None
    risk_level: Optional[str] = None
    planting_season: Optional[str] = None
    planned_start_date: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class StoreSessionResponse(BaseModel):
    success: bool
    session_id: str
    timestamp: datetime

    model_config = ConfigDict(protected_namespaces=())


@router.post("/troubleshoot", response_model=ChatResponse)
async def troubleshoot(request: ChatRequest):
    """Get farming advice from the AI advisor with persistent chat history."""
    session_id = request.session_id
    question = request.user_question

    # Get existing chat history from Redis
    chat_history = redis_get_session(session_id)

    # Check if this is context-aware mode
    is_context_aware = "[CONTEXT_AWARE_MODE]" in question
    if is_context_aware:
        question = question.replace("[CONTEXT_AWARE_MODE]", "").strip()

    # Generate response based on question and context
    response_text = generate_advice(question, chat_history, is_context_aware)

    # Append user message and AI response to history
    chat_history.append({
        "role": "user",
        "content": request.user_question,
        "timestamp": datetime.utcnow().isoformat()
    })
    chat_history.append({
        "role": "assistant",
        "content": response_text,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Save updated history back to Redis
    redis_save_session(session_id, chat_history)

    return ChatResponse(
        response=response_text,
        session_id=session_id,
        timestamp=datetime.utcnow()
    )


@router.post("/store-session", response_model=StoreSessionResponse)
async def store_session(request: StoreSessionRequest):
    """Store session context for chat continuity."""
    session_data = {
        'crop': request.crop,
        'district': request.district,
        'state': request.state,
        'soil_type': request.soil_type,
        'land_area_ha': request.land_area_ha,
        'budget_inr': request.budget_inr,
        'estimated_yield': request.estimated_yield,
        'roi': request.roi,
        'risk_level': request.risk_level,
        'planting_season': request.planting_season,
        'planned_start_date': request.planned_start_date,
        'context': request.context,
        'updated_at': datetime.utcnow().isoformat()
    }
    
    # Get existing chat history and add context as system message
    chat_history = redis_get_session(request.session_id)
    chat_history.insert(0, {
        "role": "system",
        "content": json.dumps(session_data),
        "timestamp": datetime.utcnow().isoformat()
    })
    
    redis_save_session(request.session_id, chat_history)

    return StoreSessionResponse(
        success=True,
        session_id=request.session_id,
        timestamp=datetime.utcnow()
    )


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get stored session context from Redis."""
    chat_history = redis_get_session(session_id)
    
    # Extract session data from system message if present
    session_data = {}
    if chat_history and chat_history[0].get("role") == "system":
        import json
        session_data = json.loads(chat_history[0]["content"])
    
    return {
        "session_id": session_id,
        "chat_history": chat_history,
        "session_data": session_data
    }


@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session from Redis."""
    success = redis_delete_session(session_id)
    return {"success": success, "session_id": session_id}


def generate_advice(question: str, chat_history: list, is_context_aware: bool = False) -> str:
    """Generate farming advice based on the question and optional chat context.
    
    First tries to use Gemini API for intelligent responses.
    Falls back to rule-based advice generation if API is unavailable.
    """
    # Try to import and use Gemini
    try:
        from google import genai
        from backend.core.config import settings
        
        if settings.GOOGLE_API_KEY:
            client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            
            # Build context from chat history
            context = ""
            if is_context_aware and chat_history:
                for msg in chat_history:
                    role = msg.get("role", "")
                    content = msg.get("content", "")
                    if role == "system":
                        context += f"Farm Context: {content}\n"
                    elif role == "user":
                        context += f"Farmer: {content}\n"
                    elif role == "assistant":
                        context += f"Advisor: {content}\n"
            
            prompt = f"""You are an expert agricultural advisor for Indian farmers. Speak naturally and conversationally - like a knowledgeable farmer talking to another farmer.

Context:
{context}

Question: {question}

Provide specific, practical advice suitable for Indian farming conditions. 
- Be direct and conversational, not formal or academic
- Use natural language, not bullet-point dumps
- Include relevant details like timing, quantities, and local practices
- Keep responses concise but helpful
- If you don't know something exactly, say so and suggest what to check
- NO markdown headers (##), NO bullet lists (•), NO bold/italic formatting
- Just plain, helpful conversation"""
            
            response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
            if response.text:
                return response.text.strip()
    except Exception:
        # Fall back to rule-based advice
        pass
    
    # Fallback: Rule-based advice generation
    return generate_rule_based_advice(question, chat_history, is_context_aware)


def generate_rule_based_advice(question: str, chat_history: list, is_context_aware: bool) -> str:
    """Generate farming advice using rule-based system as fallback."""
    question_lower = question.lower()
    
    # Extract farm context from system message if available
    farm_context = {}
    if chat_history and chat_history[0].get("role") == "system":
        import json
        try:
            farm_context = json.loads(chat_history[0].get("content", "{}"))
        except:
            pass
    
    crop = farm_context.get("crop", "").lower()
    district = farm_context.get("district", "").lower()
    soil_type = farm_context.get("soil_type", "").lower()
    
    # Irrigation advice
    if any(keyword in question_lower for keyword in ["irrigat", "water", "watering", "moisture", "dry", "drought"]):
        return generate_irrigation_advice(crop, soil_type, district)
    
    # Fertilizer advice
    if any(keyword in question_lower for keyword in ["fertiliz", "nutrient", "nitrogen", "phosphorus", "potassium", "npk", "urea", "dap", "mop"]):
        return generate_fertilizer_advice(crop, soil_type)
    
    # Pest/Disease advice
    if any(keyword in question_lower for keyword in ["pest", "disease", "insect", "bug", "fungus", "blight", "rot", "wilt", "yellow", "spot", "hole", "eat", "damage", "control", "treat", "manage", "prevent", "stem", "borer", "worm", "caterpillar", "larvae", "grub", "aphid", "whitefly", "hopper", "fly", "moth", "butterfly", "beetle", "weevil", "termite", "nematode", "mite", "thrips", "leafminer", "armyworm", "cutworm", "bollworm", "podborer", "shootborer", "rootworm", "wireworm"]):
        return generate_pest_disease_advice(crop, question_lower)
    
    # Harvest advice
    if any(keyword in question_lower for keyword in ["harvest", "yield", "reap", "cut", "pick", "collect", "ready", "mature"]):
        return generate_harvest_advice(crop)
    
    # Soil advice
    if any(keyword in question_lower for keyword in ["soil", "ph", "acidic", "alkaline", "saline", "sandy", "clay", "loam", "fertility", "organic"]):
        return generate_soil_advice(soil_type, crop)
    
    # Weather/Climate advice
    if any(keyword in question_lower for keyword in ["weather", "rain", "monsoon", "temperature", "heat", "cold", "frost", "humid", "climate", "season"]):
        return generate_weather_advice(crop, district)
    
    # General farming advice
    return generate_general_advice(crop, district, soil_type)


def generate_irrigation_advice(crop: str, soil_type: str, district: str) -> str:
    """Generate irrigation-specific advice."""
    advice = "## Irrigation Advice\n\n"
    
    crop_specific = {
        "rice": "Rice requires 1200-1500mm water. Maintain 5cm standing water during tillering to flowering. Drain 7-10 days before harvest.",
        "wheat": "Wheat needs 350-450mm water. Critical stages: CRI (21 days), tillering, jointing, booting, flowering, grain filling. 4-6 irrigations typically needed.",
        "cotton": "Cotton needs 700-1200mm. Avoid waterlogging. Critical: squaring, flowering, boll development. Drip irrigation saves 30-40% water.",
        "sugarcane": "Sugarcane needs 1500-2500mm. High water requirement. Furrow or drip irrigation. Critical: germination, tillering, grand growth.",
        "maize": "Maize needs 500-800mm. Critical: knee-high stage, tasseling, silking, grain filling. Avoid waterlogging.",
        "pulses": "Pulses need 300-500mm. Sensitive to waterlogging. One irrigation at flowering, one at pod filling if no rain.",
        "oilseeds": "Oilseeds need 300-500mm. Mustard/rapeseed: 2-3 irrigations. Groundnut: critical at pegging and pod development.",
    }
    
    if crop in crop_specific:
        advice += f"**{crop.title()}**: {crop_specific[crop]}\n\n"
    else:
        advice += "**General**: Most crops need irrigation at critical growth stages. Monitor soil moisture at 15-30cm depth.\n\n"
    
    if soil_type:
        soil_advice = {
            "sandy": "Sandy soil: Frequent, light irrigation (water drains fast). Increase frequency by 30-50%.",
            "clay": "Clay soil: Less frequent, heavier irrigation (holds water). Avoid waterlogging.",
            "loam": "Loam soil: Ideal water retention. Standard irrigation schedule works well.",
            "black": "Black cotton soil: High water retention. Deep, less frequent irrigation. Crack management needed.",
            "red": "Red soil: Moderate retention. Regular irrigation needed.",
            "laterite": "Laterite soil: Low retention, acidic. Frequent light irrigation + lime if needed.",
        }
        for key, val in soil_advice.items():
            if key in soil_type:
                advice += f"**Soil ({soil_type})**: {val}\n\n"
                break
    
    advice += "**Water-saving tips**:\n"
    advice += "• Use drip/sprinkler irrigation (saves 30-50% water)\n"
    advice += "• Mulch with straw/leaves to reduce evaporation\n"
    advice += "• Irrigate early morning or late evening\n"
    advice += "• Schedule based on crop stage, not calendar\n"
    advice += "• Use tensiometer or soil moisture sensor\n"
    
    return advice


def generate_fertilizer_advice(crop: str, soil_type: str) -> str:
    """Generate fertilizer-specific advice."""
    advice = "## Fertilizer & Nutrient Management\n\n"
    
    crop_npk = {
        "rice": {"n": "100-120", "p": "50-60", "k": "50-60", "note": "Split N: 50% basal, 25% tillering, 25% panicle initiation"},
        "wheat": {"n": "120-150", "p": "60-80", "k": "40-60", "note": "Split N: 50% basal, 50% at first irrigation (CRI)"},
        "cotton": {"n": "100-120", "p": "50-60", "k": "50-60", "note": "Split N: 25% basal, 50% squaring, 25% flowering. Add Mg, S, Zn"},
        "sugarcane": {"n": "250-300", "p": "100-120", "k": "150-200", "note": "Split N: 20% basal, 40% tillering, 40% grand growth. High K for cane quality"},
        "maize": {"n": "150-180", "p": "70-80", "k": "60-70", "note": "Split N: 25% basal, 50% knee-high, 25% tasseling. Zn critical"},
        "pulses": {"n": "20-25", "p": "50-60", "k": "20-30", "note": "Low N (nitrogen fixation). Rhizobium inoculation essential. P critical."},
        "groundnut": {"n": "20-30", "p": "50-60", "k": "40-50", "note": "Ca (gypsum) at pegging critical. Rhizobium inoculation. Low N."},
        "mustard": {"n": "80-100", "p": "40-50", "k": "30-40", "note": "S (sulfur) 20-30 kg/ha essential. Split N: 50% basal, 50% branching"},
    }
    
    if crop in crop_npk:
        npk = crop_npk[crop]
        advice += f"**{crop.title()} NPK (kg/ha)**: N:{npk['n']} P:{npk['p']} K:{npk['k']}\n"
        advice += f"**Schedule**: {npk['note']}\n\n"
    else:
        advice += "**General NPK**: Soil test based. Typical: N:P:K = 4:2:1 ratio for cereals.\n\n"
    
    advice += "**Key principles**:\n"
    advice += "• Always soil test before fertilizing\n"
    advice += "• Use balanced fertilization (NPK + secondary + micronutrients)\n"
    advice += "• Split nitrogen application (2-3 splits)\n"
    advice += "• Apply P & K as basal\n"
    advice += "• Add organic matter (FYM 10-15 t/ha)\n"
    advice += "• Micronutrients: Zn, Fe, Mn, Cu, B, Mo as per soil test\n"
    advice += "• Biofertilizers: Rhizobium, Azotobacter, PSB, blue-green algae\n"
    
    return advice


def generate_pest_disease_advice(crop: str, question: str) -> str:
    """Generate pest/disease-specific advice."""
    advice = "## Pest & Disease Management\n\n"
    
    pest_keywords = {
        "stem borer": "Stem borer: Dead hearts, white heads. Control: Trichocards (Trichogramma), pheromone traps, resistant varieties, insecticides at economic threshold.",
        "brown planthopper": "BPH: Honeydew, sooty mold, hopperburn. Control: Resistant varieties, avoid excess N, alternate wetting/drying, buprofezin/dinotefuran if needed.",
        "leaf folder": "Leaf folder: Folded leaves, scraping. Control: Light traps, Trichogramma, chlorantraniliprole if severe.",
        "blast": "Rice blast: Diamond-shaped lesions. Control: Resistant varieties, balanced N, avoid excess water, tricyclazole/isoprothiolane.",
        "blight": "Bacterial leaf blight: Yellow stripes, wilting. Control: Resistant varieties, field sanitation, copper compounds, avoid injury.",
        "rust": "Rust: Orange/brown pustules. Control: Resistant varieties, early sowing, propiconazole/tebuconazole.",
        "bollworm": "Bollworm: Flared squares, damaged bolls. Control: Bt cotton, pheromone traps, Trichogramma, emamectin benzoate.",
        "aphid": "Aphids: Sticky leaves, curling. Control: Ladybird beetles, neem oil, imidacloprid if severe.",
        "whitefly": "Whitefly: Yellowing, sooty mold, virus vector. Control: Yellow sticky traps, neem, spiromesifen.",
        "termite": "Termites: Wilting, hollow stems. Control: Fipronil/chlorpyrifos seed treatment, neem cake, destroy mounds.",
        "nematode": "Nematodes: Stunted, yellowing, galled roots. Control: Crop rotation, marigold, carbofuran, solarization.",
    }
    
    matched = False
    for pest, control in pest_keywords.items():
        if pest in question:
            advice += f"**{pest.title()}**: {control}\n\n"
            matched = True
    
    if not matched:
        advice += "**General IPM (Integrated Pest Management) approach**:\n"
        advice += "1. **Monitor**: Regular field scouting, pheromone traps, yellow sticky traps\n"
        advice += "2. **Identify**: Correct pest/disease identification before action\n"
        advice += "3. **Threshold**: Apply chemicals only at Economic Threshold Level (ETL)\n"
        advice += "4. **Cultural**: Crop rotation, resistant varieties, timely sowing, field sanitation\n"
        advice += "5. **Biological**: Conserve natural enemies, release Trichogramma, NPV, Bacillus thuringiensis\n"
        advice += "6. **Chemical**: Last resort. Rotate modes of action. Follow PHI (pre-harvest interval)\n\n"
        
        if crop:
            crop_pests = {
                "rice": "Common: Stem borer, BPH, leaf folder, blast, blight, tungro",
                "wheat": "Common: Rust (yellow/brown/black), aphids, termites, loose smut",
                "cotton": "Common: Bollworm, aphid, whitefly, jassid, leaf curl virus",
                "sugarcane": "Common: Early shoot borer, top borer, pyrilla, red rot, wilt",
                "maize": "Common: Stem borer, fall armyworm, downy mildew, leaf blight",
                "pulses": "Common: Pod borer, aphid, wilt, yellow mosaic virus",
            }
            if crop in crop_pests:
                advice += f"**{crop.title()} specific**: {crop_pests[crop]}\n\n"
    
    advice += "**Safety**: Always read label. Wear PPE. Observe PHI. Don't spray during flowering (bee safety).\n"
    
    return advice
def generate_harvest_advice(crop: str) -> str:
    """Generate harvest-specific advice."""
    advice = "## Harvest & Post-Harvest Management\n\n"
    
    crop_harvest = {
        "rice": "Harvest at 20-25% grain moisture (80-85% grains straw-colored). Thresh within 24h. Dry to 12-14% for storage. Yield loss 5-10% if delayed.",
        "wheat": "Harvest at 18-20% moisture (grains hard, straw golden). Combine harvest preferred. Dry to 12% for storage. Avoid rain at harvest.",
        "cotton": "Pick at fully open bolls (3-4 pickings). Morning picking for quality. Grade separately. Store dry, ventilated.",
        "sugarcane": "Harvest at 10-12 months (brix >18%). Cut at ground level. Crush within 24h. Avoid burning.",
        "maize": "Harvest at 20-25% kernel moisture (black layer formed). Shell at 15% moisture. Dry to 13% for storage.",
        "pulses": "Harvest when 80% pods brown (shattering risk). Morning harvest. Dry to 10-12% moisture.",
        "groundnut": "Harvest when pods mature (inner shell dark). Dry in windrows 2-3 days. Strip pods. Dry to 8-10%.",
        "mustard": "Harvest when 75% pods yellow-brown. Morning to avoid shattering. Dry to 8-9% moisture.",
    }
    
    if crop in crop_harvest:
        advice += f"**{crop.title()}**: {crop_harvest[crop]}\n\n"
    else:
        advice += "**General**: Harvest at physiological maturity. Use proper tools. Minimize damage. Dry properly before storage.\n\n"
    
    advice += "**Post-harvest checklist**:\n"
    advice += "• Clean produce (remove debris, damaged grains)\n"
    advice += "• Dry to safe moisture level (cereals 12-14%, pulses 10-12%, oilseeds 8-9%)\n"
    advice += "• Grade and sort for better price\n"
    advice += "• Store in clean, dry, ventilated structures\n"
    advice += "• Use hermetic bags or metal bins for long storage\n"
    advice += "• Treat storage structure (malathion spray, aluminum phosphide fumigation if needed)\n"
    advice += "• Monitor regularly for pests, moisture, temperature\n"
    
    return advice


def generate_soil_advice(soil_type: str, crop: str) -> str:
    """Generate soil-specific advice."""
    advice = "## Soil Health & Management\n\n"
    
    if soil_type:
        soil_info = {
            "sandy": "Sandy soil: Low water/nutrient retention. Add organic matter (FYM/compost 10-15 t/ha). Frequent light irrigation. Green manuring. Mulch heavily.",
            "clay": "Clay soil: High retention but poor drainage/aeration. Add gypsum (2-5 t/ha) for sodic clay. Organic matter improves structure. Avoid compaction. Raised beds.",
            "loam": "Loam soil: Ideal for most crops. Maintain with regular organic matter. Balanced fertilization. Good drainage and aeration.",
            "black": "Black cotton soil: High shrink-swell. Crack management. Deep plowing in summer. Gypsum if sodic. Wide-spaced crops. Avoid waterlogging.",
            "red": "Red soil: Acidic, low CEC. Lime (2-4 t/ha) if pH <5.5. High P fixation - band placement. Organic matter critical. Micronutrient deficiencies common.",
            "laterite": "Laterite: Highly acidic, low fertility. Heavy liming. High organic matter. Split fertilizers. Acid-tolerant crops (cashew, mango, tea).",
            "alluvial": "Alluvial: Fertile, young soils. Good response to fertilizers. Watch for micronutrient depletion over time. Regular soil testing.",
            "desert": "Desert soil: Sandy, alkaline, low organic matter. Windbreaks. Drip irrigation. Salt-tolerant crops. Heavy organic amendments.",
            "peat": "Peaty soil: High organic, acidic. Drainage needed. Liming. Suitable for rice, vegetables after improvement.",
        }
        for key, val in soil_info.items():
            if key in soil_type:
                advice += f"**{soil_type.title()} soil**: {val}\n\n"
                break
    
    if crop:
        crop_soil = {
            "rice": "Prefers clay/clay loam, pH 5.5-6.5, puddled conditions. Tolerates flooding.",
            "wheat": "Prefers loam/clay loam, pH 6.0-7.5, well-drained. Sensitive to salinity.",
            "cotton": "Prefers deep black/loam, pH 5.8-8.0, well-drained. Sensitive to waterlogging.",
            "sugarcane": "Prefers deep loam/clay loam, pH 6.0-7.5, good drainage. High nutrient demand.",
            "maize": "Prefers well-drained loam, pH 5.5-7.0. Sensitive to waterlogging and acidity.",
            "pulses": "Prefers well-drained loam, pH 6.0-7.5. Rhizobium needs neutral pH. Sensitive to salinity.",
        }
        if crop in crop_soil:
            advice += f"**{crop.title()} soil preference**: {crop_soil[crop]}\n\n"
    
    advice += "**Universal soil health practices**:\n"
    advice += "• Test soil every 2-3 years (pH, EC, OC, NPK, micros)\n"
    advice += "• Maintain organic carbon >0.5% (ideally 0.75-1%)\n"
    advice += "• Practice crop rotation (cereal-legume-oilseed)\n"
    advice += "• Green manuring (dhaincha, sunhemp, sesbania)\n"
    advice += "• Conservation agriculture: minimum till, residue retention, rotation\n"
    advice += "• Biochar for long-term carbon sequestration\n"
    advice += "• Balanced fertilization based on soil test (STCR approach)\n"
    
    return advice
def generate_weather_advice(crop: str, district: str) -> str:
    """Generate weather/climate-specific advice."""
    advice = "## Weather & Climate Smart Agriculture\n\n"
    
    advice += "**Monsoon preparedness**:\n"
    advice += "• Pre-monsoon: Land preparation, seed procurement, drainage cleaning\n"
    advice += "• Early monsoon: Timely sowing, weed management, basal fertilizer\n"
    advice += "• Mid-monsoon: Top dressing, pest monitoring, water management\n"
    advice += "• Late monsoon: Disease management, harvest planning\n"
    advice += "• Post-monsoon: Rabi sowing, soil moisture conservation\n\n"
    
    advice += "**Extreme weather management**:\n"
    advice += "• **Drought**: Drought-tolerant varieties, mulching, drip irrigation, antitranspirants, life-saving irrigation\n"
    advice += "• **Flood/Waterlogging**: Drainage channels, raised beds, submergence-tolerant varieties (Swarna Sub1 for rice), post-flood N top-up\n"
    advice += "• **Heat wave**: Light irrigation, mulching, shade nets for vegetables, avoid spraying at peak heat\n"
    advice += "• **Cold wave/Frost**: Smoke/fogging, irrigation before frost, windbreaks, tolerant varieties\n"
    advice += "• **Hail**: Hail nets for high-value crops, prompt harvest if near maturity, fungicide after hail injury\n"
    advice += "• **Cyclone**: Early harvest if possible, propping/lodging prevention, drainage\n\n"
    
    if crop:
        climate_crop = {
            "rice": "Kharif rice: Sow with monsoon onset. Transplant 21-25 DAS. Avoid late transplanting (yield loss). Rabi rice needs assured irrigation.",
            "wheat": "Rabi wheat: Timely sow (Nov 1-15 ideal). Late sowing loses 1% yield/day. Heat stress at grain fill reduces yield.",
            "cotton": "Kharif cotton: Sow pre-monsoon (Apr-May) or with monsoon. Long duration. Avoid late sowing (pink bollworm risk).",
            "sugarcane": "Plant: Feb-Mar (spring) or Oct-Nov (autumn). Ratoon management critical. Waterlogging sensitive.",
            "maize": "Kharif: With monsoon. Rabi: Oct-Nov (needs irrigation). Spring: Jan-Feb (high yield with irrigation).",
            "pulses": "Kharif: Arhar, moong, urad with monsoon. Rabi: Chickpea, lentil, pea (Oct-Nov). Moisture conservation critical.",
        }
        if crop in climate_crop:
            advice += f"**{crop.title()} climate calendar**: {climate_crop[crop]}\n\n"
    
    advice += "**Climate information sources**:\n"
    advice += "• IMD (India Meteorological Department) - district forecasts\n"
    advice += "• Meghdoot app - crop-specific advisories\n"
    advice += "• Kisan Call Centre (1800-180-1551)\n"
    advice += "• State agricultural university KVKs\n"
    advice += "• Weather-based crop insurance (PMFBY)\n"
    
    return advice


def generate_general_advice(crop: str, district: str, soil_type: str) -> str:
    """Generate general farming advice."""
    advice = "## General Farming Advisory\n\n"
    
    if crop:
        advice += f"**Crop: {crop.title()}**\n"
        advice += f"For specific {crop} advice, ask about irrigation, fertilizer, pests, harvest, or soil management.\n\n"
    
    if district:
        advice += f"**Location: {district.title()}**\n"
        advice += "Consult local KVK (Krishi Vigyan Kendra) for district-specific varieties and practices.\n\n"
    
    if soil_type:
        advice += f"**Soil: {soil_type.title()}**\n"
        advice += "Get soil tested for precise fertilizer recommendations.\n\n"
    
    advice += "**Essential farming practices**:\n"
    advice += "1. **Planning**: Crop calendar, variety selection, input procurement\n"
    advice += "2. **Soil health**: Test, organic matter, balanced nutrition\n"
    advice += "3. **Seed**: Quality seed, treatment, correct rate/spacing\n"
    advice += "4. **Water**: Efficient irrigation, scheduling, conservation\n"
    advice += "5. **Protection**: IPM, monitoring, threshold-based decisions\n"
    advice += "6. **Harvest**: Timely, proper method, post-harvest care\n"
    advice += "7. **Marketing**: Grade, store, collective marketing, value addition\n"
    advice += "8. **Records**: Maintain field diary for learning & schemes\n\n"
    
    advice += "**Government schemes to explore**:\n"
    advice += "• PM-KISAN (income support)\n"
    advice += "• PMFBY (crop insurance)\n"
    advice += "• Soil Health Card\n"
    advice += "• PMKSY (irrigation)\n"
    advice += "• PKVY (organic farming)\n"
    advice += "• RKVY-RAFTAAR (infrastructure)\n"
    advice += "• State-specific schemes (check with local agriculture dept)\n\n"
    
    advice += "**Need specific help?** Ask me about:\n"
    advice += "• Irrigation schedule for your crop\n"
    advice += "• Fertilizer dose and timing\n"
    advice += "• Pest/disease identification and control\n"
    advice += "• Harvest timing and post-harvest handling\n"
    advice += "• Soil improvement for your soil type\n"
    advice += "• Weather-based decisions\n"
    advice += "• Variety selection for your region\n"
    
    return advice