import requests
import re

# Check MAUSAM climate services page
url = 'https://mausam.imd.gov.in/responsive/climate_services.php'
try:
    r = requests.get(url, timeout=30)
    print('Climate Services page accessible, length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    for l in links[:30]:
        print('  ' + l)
except Exception as e:
    print('Error:', e)

print()
# Check rainfall information page
url = 'https://mausam.imd.gov.in/responsive/rainfallinformation.php'
try:
    r = requests.get(url, timeout=30)
    print('Rainfall Information page accessible, length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    for l in links[:30]:
        print('  ' + l)
except Exception as e:
    print('Error:', e)

print()
# Check rainfall trend page
url = 'https://imdpune.gov.in/Reports/rainfall%20variability%20page/raintrend%20new.html'
try:
    r = requests.get(url, timeout=30)
    print('Rainfall Trend page accessible, length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    for l in links[:30]:
        print('  ' + l)
except Exception as e:
    print('Error:', e)