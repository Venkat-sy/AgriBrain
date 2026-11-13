import requests
import re
import json

# Search for specific data links on MAUSAM
url = 'https://mausam.imd.gov.in'
try:
    r = requests.get(url, timeout=30)
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    data_links = [l for l in links if any(kw in l.lower() for kw in ['data', 'download', 'rainfall', 'climate', 'supply', 'portal', 'csv', 'excel', 'netcdf'])][:30]
    print('MAUSAM data-related links:')
    for l in data_links:
        print('  ' + l)
except Exception as e:
    print('MAUSAM Error:', e)

print()
# Search IMD Pune
url = 'https://www.imdpune.gov.in'
try:
    r = requests.get(url, timeout=30)
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    data_links = [l for l in links if any(kw in l.lower() for kw in ['data', 'download', 'rainfall', 'climate', 'netcdf', 'gridded', 'csv', 'excel'])][:30]
    print('IMD Pune data-related links:')
    for l in data_links:
        print('  ' + l)
except Exception as e:
    print('IMD Pune Error:', e)

print()
# Search Soil Health Card
url = 'https://soilhealth.dac.gov.in'
try:
    r = requests.get(url, timeout=30)
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    data_links = [l for l in links if any(kw in l.lower() for kw in ['data', 'download', 'soil', 'csv', 'excel', 'report'])][:30]
    print('Soil Health Card data-related links:')
    for l in data_links:
        print('  ' + l)
except Exception as e:
    print('Soil Health Card Error:', e)

print()
# Check data.gov.in via web search approach
url = 'https://data.gov.in'
try:
    r = requests.get(url, timeout=30)
    links = re.findall(r'href=[\'"]([^\'"]*)[\'"]', r.text)
    data_links = [l for l in links if any(kw in l.lower() for kw in ['crop', 'production', 'yield', 'district', 'agriculture', 'api', 'rainfall'])][:30]
    print('data.gov.in agriculture-related links:')
    for l in data_links:
        print('  ' + l)
except Exception as e:
    print('data.gov.in Error:', e)