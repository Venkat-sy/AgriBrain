import json
with open('dataset_source_manifest.json') as f:
    d = json.load(f)
print(json.dumps(d['rainfall_data'], indent=2))