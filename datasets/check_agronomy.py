import json
with open('crop_agronomy_base.json') as f:
    data = json.load(f)
print(type(data))
if isinstance(data, dict):
    print('Keys:', list(data.keys())[:5])
    for k, v in list(data.items())[:2]:
        print(f'  {k}: {v}')
else:
    print(f'Not a dict, type: {type(data)}, length: {len(data) if hasattr(data, "__len__") else "N/A"}')