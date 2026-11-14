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
    Falls back to conversational fallback if API is unavailable.
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

            system_prompt = """You are an expert Indian agronomist. Answer the user's specific question directly, conversationally, and concisely without dumping pre-written templates.

Guidelines:
- Speak like a knowledgeable farmer talking to another farmer
- Be direct, practical, and specific to Indian conditions
- No markdown headers (##), no bullet lists (•), no bold/italic
- No generic template dumps - address the actual question asked
- If unsure, say so and suggest what to check locally
- Keep responses under 200 words unless detail is needed
- Use natural paragraph flow, not formatted sections"""

            # Use the new chat API
            chat = client.chats.create(
                model="gemini-3.8-flash",
                config={"system_instruction": system_prompt}
            )

            full_prompt = f"""Context:
 {context}

 Question: {question}"""

            response = chat.send_message(full_prompt)
            if response.text:
                return response.text.strip()
    except Exception as e:
        # Log error and fall back to conversational fallback
        print(f"Gemini API error: {e}")
        pass

    # Fallback: Conversational fallback (no markdown/templates)
    return generate_conversational_fallback(question, chat_history, is_context_aware)


def generate_conversational_fallback(question: str, chat_history: list, is_context_aware: bool) -> str:
    """Generate conversational farming advice as fallback (no markdown/templates)."""
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

    # Simple keyword-based routing to conversational responses
    if any(kw in question_lower for kw in ["irrigat", "water", "watering", "moisture", "dry", "drought"]):
        return _irrigation_conversational(crop, soil_type, district)
    if any(kw in question_lower for kw in ["fertiliz", "nutrient", "nitrogen", "phosphorus", "potassium", "npk", "urea", "dap", "mop"]):
        return _fertilizer_conversational(crop, soil_type)
    if any(kw in question_lower for kw in ["pest", "disease", "insect", "bug", "fungus", "blight", "rot", "wilt", "yellow", "spot", "hole", "eat", "damage", "control", "treat", "manage", "prevent"]):
        return _pest_conversational(crop, question_lower)
    if any(kw in question_lower for kw in ["harvest", "yield", "reap", "cut", "pick", "collect", "ready", "mature"]):
        return _harvest_conversational(crop)
    if any(kw in question_lower for kw in ["soil", "ph", "acidic", "alkaline", "saline", "sandy", "clay", "loam", "fertility", "organic"]):
        return _soil_conversational(soil_type, crop)
    if any(kw in question_lower for kw in ["weather", "rain", "monsoon", "temperature", "heat", "cold", "frost", "humid", "climate", "season"]):
        return _weather_conversational(crop, district)

    # General conversational response
    return _general_conversational(crop, district, soil_type)


def _irrigation_conversational(crop: str, soil_type: str, district: str) -> str:
    """Conversational irrigation advice without markdown."""
    base = ""
    if crop == "rice":
        base = "Rice needs standing water about 5 cm deep from tillering through flowering. You'll want to drain it 7-10 days before harvest."
    elif crop == "wheat":
        base = "Wheat typically needs 4-6 irrigations at critical stages - crown root initiation, tillering, jointing, booting, flowering, and grain filling. The first one around 21 days after sowing is crucial."
    elif crop == "cotton":
        base = "Cotton hates waterlogging. Light, frequent irrigation works best - especially at squaring, flowering, and boll development. Drip can save you 30-40% water."
    elif crop == "sugarcane":
        base = "Sugarcane is thirsty - 1500-2500 mm over the season. Critical at germination, tillering, and grand growth phase. Furrow or drip both work."
    elif crop == "maize":
        base = "Maize needs water most at knee-high stage, tasseling, silking, and grain fill. Avoid waterlogging - it rots the roots fast."
    else:
        base = "Most crops need irrigation at their critical growth stages. Check soil moisture at 15-30 cm depth - if it's dry there, it's time to water."

    if soil_type:
        if "sandy" in soil_type:
            base += " Sandy soil drains fast so you'll need more frequent, lighter irrigation."
        elif "clay" in soil_type:
            base += " Clay holds water well so go heavier but less often - watch for waterlogging."
        elif "black" in soil_type:
            base += " Black cotton soil retains moisture deeply. Deep, less frequent irrigation works; manage the cracks."
        elif "red" in soil_type:
            base += " Red soil needs regular irrigation since it doesn't hold water as long."
        elif "laterite" in soil_type:
            base += " Laterite drains quick and runs acidic. Light, frequent watering plus lime if pH is low."

    base += " Pro tip: drip or sprinkler saves 30-50% water. Mulch with straw to cut evaporation. Water early morning or late evening."
    return base


def _fertilizer_conversational(crop: str, soil_type: str) -> str:
    base = ""
    if crop == "rice":
        base = "For rice, split your nitrogen - 50% at transplanting, 25% at tillering, 25% at panicle initiation. Add full P and K at basal."
    elif crop == "wheat":
        base = "Wheat: half N at sowing, half at first irrigation (CRI stage). Full P and K at basal. If soil test shows low zinc, add 25 kg ZnSO4/ha."
    elif crop == "cotton":
        base = "Cotton needs balanced NPK - 120:60:60 kg/ha typically. Split N in 3-4 doses. Add magnesium if you're on black soil."
    elif crop == "sugarcane":
        base = "Sugarcane is a heavy feeder - 300:150:150 kg/ha NPK. Apply in 4-5 splits. Don't forget micronutrients like Fe, Zn, B."
    else:
        base = "General rule: test your soil first. Balanced NPK based on soil test beats blanket recommendations every time."

    if soil_type and "black" in soil_type:
        base += " Black soil often needs extra zinc and sulfur."
    elif soil_type and "red" in soil_type:
        base += " Red soil tends to be low in P and organic matter - build it up with compost."

    base += " Organic matter is your best friend - compost or FYM at 10-15 t/ha builds soil health long-term."
    return base


def _pest_conversational(crop: str, question: str) -> str:
    if crop == "cotton":
        return "Pink bollworm is the big one for cotton - use pheromone traps, spray neem-based or recommended insecticides at ETL. Rotate crops to break the cycle."
    elif crop == "rice":
        return "Stem borer and leaf folder are common in rice. Monitor with pheromone traps. If you see deadhearts or folded leaves, spray at economic threshold. Clean cultivation and resistant varieties help."
    elif crop == "wheat":
        return "Termites and aphids can hit wheat. Seed treatment with imidacloprid helps. For aphids, spray only if you see colonies on 10%+ plants."
    else:
        return "Identify the pest first - wrong spray wastes money and kills beneficials. Check economic threshold levels. Start with neem or biocontrol, escalate only if needed. Clean fields and crop rotation prevent most problems."


def _harvest_conversational(crop: str) -> str:
    if crop == "rice":
        return "Harvest rice when 80-85% grains are golden and moisture is around 20-22%. Too early = shattering; too late = lodging and grain breakage. Drain field 7-10 days before."
    elif crop == "wheat":
        return "Wheat is ready when grains are hard, straw is golden, and moisture is 12-14%. Bite a grain - it should crack, not crush. Combine harvest at right moisture to avoid losses."
    elif crop == "cotton":
        return "Pick cotton when bolls are fully open and fluffy. Morning picks are cleaner. Don't wait too long - open bolls attract pests and weather damage. Grade as you pick."
    elif crop == "sugarcane":
        return "Cane maturity: brix 18-20%, purity 85%+. Cut at ground level, crush within 24 hours. Ratoon management starts right after harvest."
    else:
        return "Harvest timing depends on the crop and variety. Generally: right moisture content, right maturity signs, and process quickly to preserve quality. Check with your local KVK for variety-specific guidance."


def _soil_conversational(soil_type: str, crop: str) -> str:
    if not soil_type:
        return "Get your soil tested first - it's the only way to know exactly what you need. Most KVKs and state labs do it cheap or free with a Soil Health Card."
    if "black" in soil_type:
        return "Black cotton soil is great for cotton, soybean, wheat. High water retention but cracks in summer. Add organic matter to improve structure. Watch for zinc and sulfur deficiency."
    if "red" in soil_type:
        return "Red soil drains well but is often acidic and low in organic matter. Lime if pH below 5.5. Build organic matter with green manure or compost. Good for millets, pulses, groundnut."
    if "laterite" in soil_type:
        return "Laterite is acidic, low fertility, high iron/aluminum. Lime is essential. Add lots of organic matter. Cashew, mango, rubber, tea do well here."
    if "sandy" in soil_type:
        return "Sandy soil drains fast, low nutrient holding. Split fertilizers, frequent light irrigation. Drip irrigation is ideal. Good for watermelon, groundnut, potato."
    if "loam" in soil_type:
        return "Loam is ideal - good drainage, good retention, easy to work. Most crops thrive. Maintain organic matter with crop residue and rotation."
    return f"{soil_type.title()} soil has its own quirks. Soil test will tell you exactly what's missing. Add organic matter regardless - it fixes almost everything over time."


def _weather_conversational(crop: str, district: str) -> str:
    base = "IMD and Meghdoot app give district-level forecasts - check them daily during critical stages."
    if crop == "rice":
        base += " Rice hates drought at flowering. If monsoon breaks, irrigate immediately."
    elif crop == "wheat":
        base += " Wheat needs cool temps at grain fill. Terminal heat stress in March can shrivel grain - early sowing helps."
    elif crop == "cotton":
        base += " Cotton needs warm days and cool nights. Excess rain at boll opening stains fiber."
    return base + " Kisan Call Centre (1800-180-1551) and local KVK are your best real-time sources."


def _general_conversational(crop: str, district: str, soil_type: str) -> str:
    parts = []
    if crop:
        parts.append(f"For {crop}, the key is matching variety to your planting window and managing water and nutrients at the right stages.")
    if district:
        parts.append(f"In {district}, check with your KVK for locally proven varieties and pest alerts.")
    if soil_type:
        parts.append(f"Your {soil_type} soil will need specific management - soil test tells you exactly what.")
    if not parts:
        parts.append("Tell me your crop, location, and soil type - I'll give you specific advice.")
    parts.append("What exactly are you dealing with right now? Irrigation, fertilizer, pests, harvest timing?")
    return " ".join(parts)


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