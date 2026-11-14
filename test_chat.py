import sys
for m in list(sys.modules.keys()):
    if 'backend' in m:
        sys.modules.pop(m)
from backend.api.chat import generate_advice
context = [{'role': 'system', 'content': '{"crop": "wheat", "soil_type": "loam", "district": "Ludhiana"}'}, {'role': 'user', 'content': 'What fertilizer should I use?'}]
result = generate_advice('What fertilizer should I use?', context, True)
print(result[:1000])