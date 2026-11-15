import requests
import re

# Search data.gov.in catalog for specific datasets
url = 'https://data.gov.in/catalogs'
try:
    r = requests.get(url, timeout=60)
    text = r.text
    keywords = ['crop production', 'crop yield', 'district wise', 'rainfall', 'agriculture', 'production district', 'yield district']
    for kw in keywords:
        if kw.lower() in text.lower():
            print('Found: ' + kw)
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', text)
    dataset_links = [l for l in links if '/catalog/' in l or '/dataset/' in l or '/resource/' in l][:50]
    print()
    print('Dataset links found:')
    for l in dataset_links:
        print('  ' + l)
except Exception as e:
    print('Error:', e)