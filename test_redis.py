from backend.core.redis_client import get_session, save_session
import json

# Test save and get
session_id = 'test-debug-1'
chat_history = [
    {'role': 'system', 'content': json.dumps({"crop": "rice", "district": "Ludhiana"}), 'timestamp': '2026-11-13T05:46:00.000000'},
    {'role': 'user', 'content': 'test', 'timestamp': '2026-11-13T05:46:00.000000'}
]

result = save_session(session_id, chat_history)
print(f'Save result: {result}')

retrieved = get_session(session_id)
print(f'Retrieved: {retrieved}')