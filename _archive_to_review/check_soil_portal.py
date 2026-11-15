import requests
import re

# Check Soil Health Card portal for downloadable data
url = 'https://soilhealth.dac.gov.in'
try:
    r = requests.get(url, timeout=30)
    print('Soil Health Card portal accessible')
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    print('Links found:', links)
except Exception as e:
    print('Error:', e)

print()
# Check if there are known dataset URLs for soil health card
urls_to_try = [
    'https://soilhealth.dac.gov.in/soil-health-card-dashboard',
    'https://soilhealth.dac.gov.in/reports',
    'https://soilhealth.dac.gov.in/download',
    'https://soilhealth.dac.gov.in/state-wise-data',
]
for u in urls_to_try:
    try:
        r = requests.get(u, timeout=10)
        print(u + ': ' + str(r.status_code))
        if r.status_code == 200 and len(r.text) > 1000:
            print('  Content length: ' + str(len(r.text)))
    except Exception as e:
        print(u + ': Error - ' + str(e))