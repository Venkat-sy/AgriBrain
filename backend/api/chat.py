import os
import base64
import json
import uuid
from fastapi import APIRouter, Request, HTTPException
from groq import Groq

router = APIRouter()

chat_sessions = {}
MAX_HISTORY = 20

def get_or_create_session(session_id=None):
    if session_id and session_id in chat_sessions:
        return session_id
    new_session_id = str(uuid.uuid4())
    chat_sessions[new_session_id] = []
    return new_session_id

def add_to_history(session_id, role, content):
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    chat_sessions[session_id].append({'role': role, 'content': content})
    if len(chat_sessions[session_id]) > MAX_HISTORY:
        chat_sessions[session_id] = chat_sessions[session_id][-MAX_HISTORY:]

def get_session_history(session_id):
    return chat_sessions.get(session_id, [])

@router.post('/troubleshoot')
@router.post('/troubleshoot-vision')
async def troubleshoot_chat(request: Request):
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise HTTPException(status_code=500, detail='GROQ_API_KEY is missing')
    client = Groq(api_key=api_key)
    content_type = request.headers.get('content-type', '')
    message = ''
    base64_image = None
    farm_context = ''
    session_id = None
    if 'application/json' in content_type:
        body = await request.json()
        message = body.get('message') or body.get('query') or body.get('prompt') or ''
        base64_image = body.get('image')
        farm_context = body.get('context')
        session_id = body.get('session_id')
    else:
        form = await request.form()
        message = form.get('message') or form.get('query') or form.get('user_question') or 'Analyze this agricultural query.'
        farm_context = form.get('context') or ''
        if farm_context:
            try:
                farm_context = json.loads(farm_context)
            except (TypeError, ValueError):
                pass
        session_id = form.get('session_id')
        upload_file = form.get('file') or form.get('image')
        if upload_file and hasattr(upload_file, 'read'):
            file_bytes = await upload_file.read()
            if file_bytes:
                base64_image = base64.b64encode(file_bytes).decode('utf-8')
    if not message and not base64_image:
        raise HTTPException(status_code=400, detail='Please provide a question or an image.')
    session_id = get_or_create_session(session_id)
    history = get_session_history(session_id)
    messages = [{'role': msg['role'], 'content': msg['content']} for msg in history]
    user_content = message
    if farm_context:
        if not isinstance(farm_context, str):
            import json
            farm_context = json.dumps(farm_context, indent=2)
        user_content = 'Farm Context: ' + farm_context + chr(10) + chr(10) + 'User Query: ' + message
    if base64_image:
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
        messages.append({'role': 'user', 'content': [{'type': 'text', 'text': 'You are an expert Indian plant pathologist and agronomist. Diagnose this image and answer directly with exact remedies and dosages: ' + user_content}, {'type': 'image_url', 'image_url': {'url': 'data:image/jpeg;base64,' + base64_image}}]})
    else:
        if not messages:
            system_prompt = 'You are AgriBrain, an elite AI Agronomist for Indian farming. Give direct, practical, scientific answers immediately with exact numerical ranges (temperature in C, NPK in kg/ha, soil pH, seed rate, irrigation schedule, and Indian market/MSP insights). NEVER respond with a generic template asking the user for their crop or location.'
            if farm_context:
                system_prompt += chr(10) + 'Active Farm Digital Twin Context: ' + farm_context
            messages.insert(0, {'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': user_content})
    try:
        if base64_image:
            completion = client.chat.completions.create(model='llama-3.2-11b-vision-preview', messages=messages, temperature=0.4, max_tokens=900)
        else:
            completion = client.chat.completions.create(model='llama3-70b-8192', messages=messages, temperature=0.5, max_tokens=900)
        reply = completion.choices[0].message.content
        add_to_history(session_id, 'user', user_content)
        add_to_history(session_id, 'assistant', reply)
        return {'response': reply, 'reply': reply, 'message': reply, 'status': 'success', 'session_id': session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail='Groq AI Error: ' + str(e))

@router.get('/session/{session_id}')
async def get_session(session_id: str):
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail='Session not found')
    return {'session_id': session_id, 'history': chat_sessions[session_id]}

@router.delete('/session/{session_id}')
async def delete_session(session_id: str):
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    return {'status': 'success', 'message': 'Session deleted'}
