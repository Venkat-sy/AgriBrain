import requests
import re

# Check IMD API reference
url = 'https://api.imd.gov.in/public/api_reference.html'
try:
    r = requests.get(url, timeout=30)
    print('IMD API reference accessible, length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    for l in links[:50]:
        print('  ' + l)
except Exception as e:
    print('Error:', e)

# Check data.gov.in catalog
url = 'https://data.gov.in/catalogs'
try:
    r = requests.get(url, timeout=30)
    print()
    print('data.gov.in catalogs accessible, length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    for l in links[:50]:
        if any(kw in l.lower() for kw in ['crop', 'production', 'yield', 'district', 'agriculture', 'rainfall', 'soil']):
            print('  ' + l)
except Exception as e:
    print('Error:', e)