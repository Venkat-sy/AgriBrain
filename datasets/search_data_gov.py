import requests
import re

url = 'https://data.gov.in/search/site?keys=crop%20production%20district'
try:
    r = requests.get(url, timeout=30)
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    for l in links:
        if any(kw in l.lower() for kw in ['dataset', 'catalog', 'resource', 'crop', 'production', 'yield', 'district']) and 'javascript' not in l:
            print(l)
except Exception as e:
    print('Error:', e)