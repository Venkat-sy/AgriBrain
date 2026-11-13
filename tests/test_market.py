import sys
sys.path.insert(0, '.')
from backend.services.market_pricing import fetch_live_market_price
import asyncio

crops = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane', 'Jute', 'Coffee', 'Banana', 'Mango', 'Apple']
for c in crops:
    try:
        price = fetch_live_market_price(c, 'Punjab')
        print(f'{c}: Rs{price:,.0f}/ton')
    except Exception as e:
        print(f'{c}: ERROR - {e}')