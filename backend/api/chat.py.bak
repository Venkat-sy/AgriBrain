from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any, List
from datetime import datetime
import json
import os
import base64

from backend.core.redis_client import get_session as redis_get_session, save_session as redis_save_session, delete_session as redis_delete_session
from groq import Groq
from backend.core.config import settings

router = APIRouter(prefix='/api/v1/chat', tags=['chat'])

# Groq client initialized lazily inside route handlers — ZERO global client
def get_groq_client():
    """Get Groq client lazily. Raises ValueError if key missing."""
    api_key = os.getenv("GROQ_API_KEY") or settings.GROQ_API_KEY
    if not api_key:
        raise ValueError("GROQ_API_KEY not configured. Set it in .env or environment variables.")
    return Groq(api_key=api_key)


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


# ─── Text-only troubleshoot endpoint ──────────────────────────────────────

@router.post("/troubleshoot", response_model=ChatResponse)
async def troubleshoot(request: ChatRequest):
    """Get farming advice from the AI advisor with persistent chat history."""
    session_id = request.session_id
    question = request.user_question

    chat_history = redis_get_session(session_id)

    is_context_aware = "[CONTEXT_AWARE_MODE]" in question
    if is_context_aware:
        question = question.replace("[CONTEXT_AWARE_MODE]", "").strip()

    response_text = await generate_advice(question, chat_history, is_context_aware)

    chat_history.append({"role": "user", "content": request.user_question, "timestamp": datetime.utcnow().isoformat()})
    chat_history.append({"role": "assistant", "content": response_text, "timestamp": datetime.utcnow().isoformat()})

    redis_save_session(session_id, chat_history)

    return ChatResponse(response=response_text, session_id=session_id, timestamp=datetime.utcnow())


# ─── Vision troubleshoot endpoint (spec §5) ───────────────────────────────

@router.post("/troubleshoot-vision", response_model=ChatResponse)
async def troubleshoot_vision(
    session_id: str = Form(...),
    user_question: str = Form(...),
    file: UploadFile = File(None)
):
    """
    Multimodal farming advice per AGRIBRAIN_STRICT_SPEC.txt §5.
    - If file provided: use llama-3.2-11b-vision-preview with base64 image.
    - If no file: use llama-3.1-8b-instant text-only.
    """
    chat_history = redis_get_session(session_id)
    is_context_aware = "[CONTEXT_AWARE_MODE]" in user_question
    if is_context_aware:
        user_question = user_question.replace("[CONTEXT_AWARE_MODE]", "").strip()

    if file is not None:
        # Validate image type
        if file.content_type and not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        file_bytes = await file.read()
        base64_image = base64.b64encode(file_bytes).decode("utf-8")
        content_type = file.content_type or "image/jpeg"

        try:
            # Initialize client INSIDE function — ZERO global Groq
            client = get_groq_client()
            response = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert Indian agronomist. Analyze crop/soil images and provide specific, actionable farming advice for Indian conditions."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": user_question},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:{content_type};base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                temperature=0.7,
                max_tokens=1024,
            )
            response_text = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[Groq Vision] Error: {e}")
            response_text = await generate_advice(user_question, chat_history, is_context_aware)
            response_text = f"[Image analysis unavailable: {str(e)}]\n\n{response_text}"

        chat_history.append({"role": "user", "content": f"[Image uploaded] {user_question}", "timestamp": datetime.utcnow().isoformat()})
    else:
        # Text-only path
        response_text = await generate_advice(user_question, chat_history, is_context_aware)
        chat_history.append({"role": "user", "content": user_question, "timestamp": datetime.utcnow().isoformat()})

    chat_history.append({"role": "assistant", "content": response_text, "timestamp": datetime.utcnow().isoformat()})
    redis_save_session(session_id, chat_history)

    return ChatResponse(response=response_text, session_id=session_id, timestamp=datetime.utcnow())


# ─── Session management ────────────────────────────────────────────────────

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

    chat_history = redis_get_session(request.session_id)
    chat_history.insert(0, {
        "role": "system",
        "content": json.dumps(session_data),
        "timestamp": datetime.utcnow().isoformat()
    })

    redis_save_session(request.session_id, chat_history)

    return StoreSessionResponse(success=True, session_id=request.session_id, timestamp=datetime.utcnow())


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get stored session context from Redis."""
    chat_history = redis_get_session(session_id)

    session_data = {}
    if chat_history and chat_history[0].get("role") == "system":
        try:
            session_data = json.loads(chat_history[0]["content"])
        except Exception:
            pass

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


# ─── Core LLM advice function ──────────────────────────────────────────────

async def generate_advice(question: str, chat_history: list, is_context_aware: bool = False) -> str:
    """
    Generate farming advice using Groq llama-3.1-8b-instant.
    Client initialized inside this function — ZERO global client.
    """
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

    system_prompt = """You are an expert Indian agronomist. Answer the user's question directly, fluently, and conversationally based on their specific soil type and location. Do NOT use generic markdown templates, do NOT output '## Soil Health', and do NOT use pre-written bullet points. Talk to the user like a human expert giving tailored advice."""

    messages = [{"role": "system", "content": system_prompt}]
    if context:
        messages.append({"role": "user", "content": f"Context:\n{context}"})
    messages.append({"role": "user", "content": question})

    try:
        client = get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=1024,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[Groq] Error: {e}")
        return generate_conversational_fallback(question, chat_history, is_context_aware)


# ─── Conversational fallback (no Groq) ────────────────────────────────────

def generate_conversational_fallback(question: str, chat_history: list, is_context_aware: bool) -> str:
    """Generate conversational farming advice as offline fallback."""
    question_lower = question.lower()

    farm_context: dict = {}
    if chat_history and chat_history[0].get("role") == "system":
        try:
            farm_context = json.loads(chat_history[0].get("content", "{}"))
        except Exception:
            pass

    crop = farm_context.get("crop", "").lower()
    district = farm_context.get("district", "").lower()
    soil_type = farm_context.get("soil_type", "").lower()

    if any(kw in question_lower for kw in ["irrigat", "water", "watering", "moisture", "dry", "drought"]):
        return _irrigation_conversational(crop, soil_type, district)
    if any(kw in question_lower for kw in ["fertiliz", "nutrient", "nitrogen", "phosphorus", "potassium", "npk", "urea", "dap"]):
        return _fertilizer_conversational(crop, soil_type)
    if any(kw in question_lower for kw in ["pest", "disease", "insect", "bug", "fungus", "blight", "rot", "wilt", "yellow", "spot"]):
        return _pest_conversational(crop, question_lower)
    if any(kw in question_lower for kw in ["harvest", "yield", "reap", "cut", "pick", "collect", "ready", "mature"]):
        return _harvest_conversational(crop)
    if any(kw in question_lower for kw in ["soil", "ph", "acidic", "alkaline", "sandy", "clay", "loam"]):
        return _soil_conversational(soil_type, crop)
    if any(kw in question_lower for kw in ["weather", "rain", "monsoon", "temperature", "heat", "cold"]):
        return _weather_conversational(crop, district)

    return _general_conversational(crop, district, soil_type)


def _irrigation_conversational(crop: str, soil_type: str, district: str) -> str:
    base = ""
    if crop == "rice":
        base = "Rice needs standing water about 5 cm deep from tillering through flowering. Drain it 7-10 days before harvest."
    elif crop == "wheat":
        base = "Wheat needs 4-6 irrigations at critical stages - crown root initiation, tillering, jointing, booting, flowering, and grain filling. The first at 21 days after sowing is crucial."
    elif crop == "cotton":
        base = "Cotton hates waterlogging. Light, frequent irrigation works best - especially at squaring, flowering, and boll development. Drip saves 30-40% water."
    elif crop == "sugarcane":
        base = "Sugarcane is thirsty - 1500-2500 mm over the season. Critical at germination, tillering, and grand growth. Furrow or drip both work."
    elif crop == "maize":
        base = "Maize needs water most at knee-high, tasseling, silking, and grain fill. Avoid waterlogging - it rots roots fast."
    else:
        base = "Most crops need irrigation at critical growth stages. Check soil moisture at 15-30 cm depth - if dry there, it's time to water."
    if "sandy" in soil_type:
        base += " Sandy soil drains fast so you'll need more frequent, lighter irrigation."
    elif "clay" in soil_type:
        base += " Clay holds water well - go heavier but less often. Watch for waterlogging."
    base += " Pro tip: drip or sprinkler saves 30-50% water. Mulch with straw to cut evaporation."
    return base


def _fertilizer_conversational(crop: str, soil_type: str) -> str:
    base = ""
    if crop == "rice":
        base = "For rice, split your nitrogen - 50% at transplanting, 25% at tillering, 25% at panicle initiation. Add full P and K at basal."
    elif crop == "wheat":
        base = "Wheat: half N at sowing, half at first irrigation (CRI stage). Full P and K at basal. Add 25 kg ZnSO4/ha if soil test shows low zinc."
    elif crop == "cotton":
        base = "Cotton needs balanced NPK - 120:60:60 kg/ha. Split N in 3-4 doses. Add magnesium on black soil."
    elif crop == "sugarcane":
        base = "Sugarcane is a heavy feeder - 300:150:150 kg/ha NPK. Apply in 4-5 splits. Don't skip micronutrients like Fe, Zn, B."
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
        return "Pink bollworm is the big one for cotton - use pheromone traps, spray neem-based insecticides at ETL. Rotate crops to break the cycle."
    elif crop == "rice":
        return "Stem borer and leaf folder are common in rice. Monitor with pheromone traps. If you see deadhearts or folded leaves, spray at economic threshold."
    elif crop == "wheat":
        return "Termites and aphids can hit wheat. Seed treatment with imidacloprid helps. For aphids, spray only if colonies appear on 10%+ plants."
    else:
        return "Identify the pest first - wrong spray wastes money and kills beneficials. Check economic threshold levels. Start with neem or biocontrol, escalate only if needed."


def _harvest_conversational(crop: str) -> str:
    if crop == "rice":
        return "Harvest rice when 80-85% grains are golden and moisture is around 20-22%. Too early = shattering; too late = lodging. Drain field 7-10 days before."
    elif crop == "wheat":
        return "Wheat is ready when grains are hard, straw is golden, moisture is 12-14%. Bite a grain - it should crack, not crush."
    elif crop == "cotton":
        return "Pick cotton when bolls are fully open and fluffy. Morning picks are cleaner. Grade as you pick."
    elif crop == "sugarcane":
        return "Cane maturity: brix 18-20%, purity 85%+. Cut at ground level, crush within 24 hours."
    else:
        return "Harvest timing depends on crop and variety. Check with your local KVK for variety-specific guidance."


def _soil_conversational(soil_type: str, crop: str) -> str:
    if not soil_type:
        return "Get your soil tested first - most KVKs and state labs do it cheap or free with a Soil Health Card."
    if "black" in soil_type:
        return "Black cotton soil is great for cotton, soybean, wheat. High water retention but cracks in summer. Add organic matter to improve structure."
    if "red" in soil_type:
        return "Red soil drains well but is often acidic and low in organic matter. Lime if pH is below 5.5. Good for millets, pulses, groundnut."
    if "sandy" in soil_type:
        return "Sandy soil drains fast, low nutrient holding. Split fertilizers, frequent light irrigation. Drip is ideal. Good for watermelon, groundnut, potato."
    if "loam" in soil_type:
        return "Loam is ideal - good drainage, good retention, easy to work. Most crops thrive. Maintain organic matter with crop residue and rotation."
    return f"{soil_type.title()} soil has its own quirks. Soil test will tell you exactly what's missing."


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
