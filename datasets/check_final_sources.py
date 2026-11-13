import requests
import re

# Check ICAR data portal specifically
url = 'https://data.icar.gov.in'
try:
    r = requests.get(url, timeout=30)
    print('ICAR Data portal:', r.status_code, 'length:', len(r.text))
    if r.status_code == 200 and len(r.text) > 1000:
        links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
        for l in links[:30]:
            print('  ' + l)
except Exception as e:
    print('ICAR Data portal Error:', e)

print()
# Check for agriculture data on data.gov.in via search
url = 'https://data.gov.in/search/site?keys=crop%20production%20district'
try:
    r = requests.get(url, timeout=30)
    print('data.gov.in search:', r.status_code, 'length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    for l in links[:30]:
        if 'dataset' in l or 'catalog' in l or 'resource' in l:
            print('  ' + l)
except Exception as e:
    print('Search Error:', e)