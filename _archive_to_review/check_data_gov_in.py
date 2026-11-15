import requests
import re

# Check data.gov.in catalogs
url = 'https://data.gov.in/catalogs'
try:
    r = requests.get(url, timeout=60)
    print('Length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    catalog_links = [l for l in links if '/catalog/' in l][:20]
    print('Catalog links:', catalog_links)
except Exception as e:
    print('Error:', e)