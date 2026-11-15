import json
with open('district_rainfall_summary.json') as f:
    d = json.load(f)
print(list(d.keys())[:5])
print(json.dumps(d['ADILABAD_ANDHRA PRADESH'], indent=2))