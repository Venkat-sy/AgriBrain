import sys
for m in list(sys.modules.keys()):
    if 'backend' in m:
        sys.modules.pop(m)
from backend.api.chat import generate_advice
context = [{'role': 'system', 'content': '{"crop": "rice", "soil_type": "clay", "district": "Cuttack"}'}]
result = generate_advice('When should I transplant rice seedlings?', context, True)
print('Response type:', type(result).__name__)
print('Has markdown:', '##' in result)
print('Has bullets:', '•' in result)
print('Length:', len(result))
print('First 500 chars:', result[:500])