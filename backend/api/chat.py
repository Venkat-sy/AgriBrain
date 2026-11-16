import os
import base64
from fastapi import APIRouter, Request, HTTPException
from groq import Groq

router = APIRouter()

@router.post("/troubleshoot")
@router.post("/troubleshoot-vision")
async def troubleshoot_chat(request: Request):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY is missing in Render environment variables.")

    client = Groq(api_key=api_key)
    content_type = request.headers.get("content-type", "")

    message = ""
    base64_image = None
    farm_context = ""

    if "application/json" in content_type:
        body = await request.json()
        message = body.get("message") or body.get("query") or body.get("prompt") or ""
        base64_image = body.get("image")
        farm_context = body.get("context") or ""
    else:
        form = await request.form()
        message = form.get("message") or form.get("query") or "Analyze this agricultural query."
        farm_context = form.get("context") or ""
        upload_file = form.get("file") or form.get("image")
        if upload_file and hasattr(upload_file, "read"):
            file_bytes = await upload_file.read()
            if file_bytes:
                base64_image = base64.b64encode(file_bytes).decode("utf-8")

    if not message and not base64_image:
        raise HTTPException(status_code=400, detail="Please provide a question or an image.")

    try:
        if base64_image:
            if "," in base64_image:
                base64_image = base64_image.split(",")[1]
            completion = client.chat.completions.create(
                model="llama-3.2-11b-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": f"You are an expert Indian plant pathologist and agronomist. Diagnose this image and answer directly with exact remedies and dosages: {message}"
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                temperature=0.4,
                max_tokens=900
            )
        else:
            system_prompt = (
                "You are AgriBrain, an elite AI Agronomist for Indian farming. "
                "Give direct, practical, scientific answers immediately with exact numerical ranges "
                "(temperature in °C, NPK in kg/ha, soil pH, seed rate, irrigation schedule, and Indian market/MSP insights). "
                "NEVER respond with a generic template asking the user for their crop or location."
            )
            if farm_context:
                system_prompt += f"\nActive Farm Digital Twin Context: {farm_context}"

            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.5,
                max_tokens=900
            )

        reply = completion.choices[0].message.content
        return {"response": reply, "reply": reply, "message": reply, "status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq AI Error: {str(e)}")
