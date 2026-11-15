import requests
import re

# Search ICAR for soil data portals
url = 'https://icar.org.in/content/soil-health'
try:
    r = requests.get(url, timeout=30)
    print('ICAR soil health:', r.status_code, 'length:', len(r.text))
    if len(r.text) > 1000:
        links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
        for l in links[:20]:
            print('  ' + l)
except Exception as e:
    print('Error:', e)

print()
# Check ICAR publications
url = 'https://icar.org.in/content/all-publications'
try:
    r = requests.get(url, timeout=30)
    print('ICAR publications:', r.status_code, 'length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    soil_pubs = [l for l in links if any(kw in l.lower() for kw in ['soil', 'survey', 'land', 'profile', 'map'])][:20]
    print('Soil-related publications:', soil_pubs)
except Exception as e:
    print('Error:', e)