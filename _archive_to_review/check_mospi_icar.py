import requests
import re

# Check for MOSPI data
url = 'https://mospi.gov.in'
try:
    r = requests.get(url, timeout=30)
    print('MOSPI accessible, length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    ag_links = [l for l in links if any(kw in l.lower() for kw in ['agriculture', 'crop', 'production', 'yield', 'data', 'download', 'statistics', 'report'])][:30]
    print('Agriculture-related links:')
    for l in ag_links:
        print('  ' + l)
except Exception as e:
    print('MOSPI Error:', e)

print()
# Check ICAR portal
url = 'https://icar.org.in'
try:
    r = requests.get(url, timeout=30)
    print('ICAR accessible, length:', len(r.text))
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    ag_links = [l for l in links if any(kw in l.lower() for kw in ['soil', 'data', 'download', 'research', 'publication', 'nbsslup'])][:30]
    print('Soil/data-related links:')
    for l in ag_links:
        print('  ' + l)
except Exception as e:
    print('ICAR Error:', e)