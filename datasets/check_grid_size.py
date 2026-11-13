import pandas as pd
import numpy as np
icrisat_years = list(range(1978, 2018))
icrisat_crops = ['Rice', 'Wheat', 'Maize', 'Sorghum', 'Pearl Millet', 'Finger Millet', 'Barley', 'Kharif Sorghum', 'Rabi Sorghum', 'Chickpea', 'Pigeonpea', 'Green Gram', 'Black Gram', 'Lentil', 'Pea', 'Groundnut', 'Soybean', 'Sunflower', 'Sesame', 'Safflower', 'Linseed', 'Castor', 'Rapeseed and Mustard', 'Cotton', 'Jute', 'Sugarcane', 'Minor Pulses', 'Oilseeds']
canonical_districts = 641
total = canonical_districts * len(icrisat_crops) * len(icrisat_years)
print(f'Total rows: {total:,}')
print(f'Memory estimate (100 bytes/row): {total * 100 / 1e9:.2f} GB')