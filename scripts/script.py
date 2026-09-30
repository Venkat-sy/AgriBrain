import json

with open('epmc_papers.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('--- INDIA PAPERS ---')
for p in data.get('india', []):
    print(f"{p.get('pubYear')} | {p.get('title')} | {p.get('journalTitle')} | {p.get('doi')}")

print('\n--- GLOBAL PAPERS ---')
for p in data.get('global', []):
    print(f"{p.get('pubYear')} | {p.get('title')} | {p.get('journalTitle')} | {p.get('doi')}")
