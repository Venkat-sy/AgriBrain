import requests
import re

# Check NBSS&LUP - try alternative URLs
urls = [
    'https://nbsslup.in',
    'https://www.nbsslup.in',
    'http://nbsslup.in',
    'http://www.nbsslup.in',
]
for u in urls:
    try:
        r = requests.get(u, timeout=30)
        print(u + ': ' + str(r.status_code) + ', length: ' + str(len(r.text)))
        if len(r.text) > 1000:
            links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
            soil_links = [l for l in links if any(kw in l.lower() for kw in ['soil', 'data', 'download', 'map', 'report', 'profile', 'survey'])][:20]
            print('  Soil/data links:', soil_links)
    except Exception as e:
        print(u + ': Error - ' + str(e))
    print()