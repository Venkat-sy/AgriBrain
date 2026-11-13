import requests
import re

# Check MAUSAM API doc
url = 'https://mausam.imd.gov.in/Forecast/marquee_data/API_doc.pdf'
try:
    r = requests.get(url, timeout=30)
    print('API Doc accessible, length:', len(r.content))
    with open('API_doc.pdf', 'wb') as f:
        f.write(r.content)
    print('Saved API_doc.pdf')
except Exception as e:
    print('Error:', e)

print()
# Check data.gov.in APIs page
url = 'https://data.gov.in/apis'
try:
    r = requests.get(url, timeout=30)
    print('data.gov.in APIs page accessible, length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    for l in links[:50]:
        if 'api' in l.lower() or 'catalog' in l.lower() or 'dataset' in l.lower():
            print('  ' + l)
except Exception as e:
    print('Error:', e)