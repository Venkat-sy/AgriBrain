import requests
import re

# Get full text of IMD API reference
url = 'https://api.imd.gov.in/public/api_reference.html'
try:
    r = requests.get(url, timeout=30)
    text = r.text
    # Find sections about rainfall
    sections = ['api-1', 'api-2', 'api-3', 'api-4', 'api-5', 'api-6', 'api-7', 'api-8', 'api-9', 'api-10',
                'api-11', 'api-12', 'api-13', 'api-14', 'api-15', 'api-16', 'api-17', 'api-18', 'api-19',
                'api-20', 'api-21', 'api-22', 'api-23', 'api-24', 'api-25', 'api-26', 'api-27', 'api-28']
    for section in sections:
        # Simple pattern - find the section div
        start = text.find('id="' + section + '"')
        if start == -1:
            start = text.find("id='" + section + "'")
        if start != -1:
            # Find next api- section or end
            end = text.find('id="api-', start + 1)
            if end == -1:
                end = text.find("id='api-", start + 1)
            if end == -1:
                end = len(text)
            content = text[start:end]
            if 'rainfall' in content.lower() or 'district' in content.lower():
                print('=== ' + section + ' ===')
                print(content[:1500])
                print()
except Exception as e:
    print('Error:', e)