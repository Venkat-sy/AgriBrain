"""Groq LLM service for cultivation timeline generation."""
from groq import Groq
from backend.core.config import settings
from typing import List, Dict, Any
import os
import json


client = Groq(api_key=os.getenv("GROQ_API_KEY", settings.GROQ_API_KEY))


async def generate_cultivation_timeline(crop_name: str) -> List[Dict[str, Any]]:
    """Generate a cultivation timeline for a crop using Groq Llama-3."""
    
    prompt = f"""Generate a detailed cultivation timeline for {crop_name} in India. 
Return ONLY a valid JSON array of stages (no other text). Each stage must have:
- stage_name: string (e.g., "Sowing & Germination")
- estimated_days: integer (number of days for this stage)
- agronomy_advice: string (specific actionable advice for this stage)

Include 5-6 stages covering the full lifecycle from sowing to harvest.
Make advice specific to Indian agricultural conditions and {crop_name}.

Example format:
[
  {{"stage_name": "Sowing & Germination", "estimated_days": 10, "agronomy_advice": "Sow at 4-5 cm depth. Apply DAP (125 kg/ha) + Urea (50 kg/ha) at sowing. Irrigate lightly after sowing."}},
  {{"stage_name": "Vegetative Stage", "estimated_days": 30, "agronomy_advice": "First irrigation at 21 days (CRI stage). Apply remaining 50% N. Monitor for termites and aphids."}}
]"""
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are an expert Indian agronomist. Provide detailed, actionable cultivation timelines in valid JSON format only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1500,
        )
        
        content = response.choices[0].message.content
        data = json.loads(content)
        
        # Handle different possible response formats
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "stages" in data:
            return data["stages"]
        elif isinstance(data, dict) and "timeline" in data:
            return data["timeline"]
        else:
            # Try to extract array from any key
            for key, value in data.items():
                if isinstance(value, list):
                    return value
            return _get_static_timeline(crop_name)
            
    except Exception as e:
        print(f"Groq timeline generation failed for {crop_name}: {e}")
        return _get_static_timeline(crop_name)


def _get_static_timeline(crop_name: str) -> List[Dict[str, Any]]:
    """Fallback static timelines for common crops."""
    from backend.api.simulation import CROP_TIMELINES
    return CROP_TIMELINES.get(crop_name.lower(), [
        {"stage_name": "Sowing", "estimated_days": 10, "agronomy_advice": "Prepare land and sow seeds."},
        {"stage_name": "Vegetative", "estimated_days": 30, "agronomy_advice": "Apply fertilizers and monitor growth."},
        {"stage_name": "Flowering", "estimated_days": 20, "agronomy_advice": "Critical water management stage."},
        {"stage_name": "Maturity", "estimated_days": 25, "agronomy_advice": "Monitor for harvest readiness."},
        {"stage_name": "Harvest", "estimated_days": 10, "agronomy_advice": "Harvest and store properly."},
    ])