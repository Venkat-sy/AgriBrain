import pandas as pd
import numpy as np
import os
import random

# Set random seed for reproducibility
np.random.seed(42)

# Parameters
NUM_SAMPLES = 10000
CROPS = ['Rice', 'Wheat', 'Maize', 'Cotton', 'Sugarcane']

# Optimal ranges for crops (Indian climate context)
# Dict structure: 'Crop': [N_opt, P_opt, K_opt, pH_min, pH_max, Rain_opt, Temp_opt, Humidity_opt, Moisture_opt]
CROP_OPTIMALS = {
    'Rice': {'N': 100, 'P': 40, 'K': 40, 'pH': [5.5, 6.5], 'Rain': 1200, 'Temp': 26, 'Hum': 80, 'Moist': 90, 'Base_Yield': 5.0},
    'Wheat': {'N': 120, 'P': 60, 'K': 40, 'pH': [6.0, 7.5], 'Rain': 400, 'Temp': 20, 'Hum': 60, 'Moist': 50, 'Base_Yield': 3.5},
    'Maize': {'N': 120, 'P': 60, 'K': 40, 'pH': [5.8, 7.5], 'Rain': 600, 'Temp': 25, 'Hum': 65, 'Moist': 60, 'Base_Yield': 4.0},
    'Cotton': {'N': 100, 'P': 50, 'K': 50, 'pH': [5.8, 8.0], 'Rain': 700, 'Temp': 28, 'Hum': 55, 'Moist': 45, 'Base_Yield': 2.0},
    'Sugarcane': {'N': 150, 'P': 60, 'K': 80, 'pH': [6.5, 7.5], 'Rain': 1500, 'Temp': 30, 'Hum': 70, 'Moist': 80, 'Base_Yield': 70.0},
}

data = []

for _ in range(NUM_SAMPLES):
    crop = random.choice(CROPS)
    opt = CROP_OPTIMALS[crop]
    
    # Simulate feature values around optimal with some random noise (some fields will be highly sub-optimal)
    # 20% chance to have a severely deficient/extreme field
    is_extreme = np.random.rand() < 0.2
    
    if is_extreme:
        N = np.random.uniform(10, opt['N'] * 1.5)
        P = np.random.uniform(5, opt['P'] * 1.5)
        K = np.random.uniform(5, opt['K'] * 1.5)
        pH = np.random.uniform(4.0, 9.0)
        Rain = np.random.uniform(100, opt['Rain'] * 1.5)
        Temp = np.random.uniform(15, 45)
        Hum = np.random.uniform(20, 95)
        Moist = np.random.uniform(10, 95)
    else:
        N = np.random.normal(opt['N'], opt['N'] * 0.2)
        P = np.random.normal(opt['P'], opt['P'] * 0.2)
        K = np.random.normal(opt['K'], opt['K'] * 0.2)
        pH = np.random.uniform(opt['pH'][0] - 0.5, opt['pH'][1] + 0.5)
        Rain = np.random.normal(opt['Rain'], opt['Rain'] * 0.2)
        Temp = np.random.normal(opt['Temp'], 3)
        Hum = np.random.normal(opt['Hum'], 10)
        Moist = np.random.normal(opt['Moist'], 10)
    
    # Clip to realistic bounds
    N = np.clip(N, 0, 300)
    P = np.clip(P, 0, 150)
    K = np.clip(K, 0, 150)
    pH = np.clip(pH, 3.5, 9.5)
    Rain = np.clip(Rain, 50, 3000)
    Temp = np.clip(Temp, 10, 48)
    Hum = np.clip(Hum, 10, 100)
    Moist = np.clip(Moist, 0, 100)
    
    # Calculate target variables based on formulas (Digital Twin logic)
    
    # Yield Penalty Logic
    penalty = 0.0
    if N < opt['N'] * 0.7: penalty += 0.2
    if P < opt['P'] * 0.7: penalty += 0.1
    if K < opt['K'] * 0.7: penalty += 0.1
    if not (opt['pH'][0] <= pH <= opt['pH'][1]): penalty += 0.15
    if abs(Temp - opt['Temp']) > 5: penalty += 0.15
    if Rain < opt['Rain'] * 0.6: penalty += 0.3
    
    penalty = min(penalty, 0.95) # Max 95% yield loss
    
    Yield = opt['Base_Yield'] * (1.0 - penalty) + np.random.normal(0, opt['Base_Yield'] * 0.05)
    Yield = max(Yield, 0.1) # Minimum yield
    
    # Irrigation Demand Logic
    # If rain is sufficient and moisture is high, demand is low. Otherwise, it spikes.
    rain_deficit = opt['Rain'] - Rain
    moist_deficit = opt['Moist'] - Moist
    
    irrigation_demand = max(0, rain_deficit * 0.5) + max(0, moist_deficit * 5)
    if irrigation_demand < 50: irrigation_demand = 0 # No irrigation needed if close to optimal
    
    # Risk Assessment Logic
    # 0 = Low Risk, 1 = Medium Risk, 2 = High Risk (Crop Failure)
    if penalty > 0.6:
        risk = 2
    elif penalty > 0.3 or irrigation_demand > (opt['Rain'] * 0.5):
        risk = 1
    else:
        risk = 0
        
    data.append({
        'Nitrogen': round(N, 2),
        'Phosphorus': round(P, 2),
        'Potassium': round(K, 2),
        'pH': round(pH, 2),
        'Rainfall_mm': round(Rain, 2),
        'Temperature_C': round(Temp, 2),
        'Humidity_pct': round(Hum, 2),
        'Soil_Moisture_pct': round(Moist, 2),
        'Crop_Type': crop,
        'Yield_tons_per_ha': round(Yield, 2),
        'Irrigation_Demand_mm': round(irrigation_demand, 2),
        'Crop_Failure_Risk': risk
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Introduce realistic missing values (e.g. faulty sensors)
# Randomly set 2% of pH and Soil_Moisture to NaN
for col in ['pH', 'Soil_Moisture_pct']:
    mask = np.random.rand(NUM_SAMPLES) < 0.02
    df.loc[mask, col] = np.nan

output_path = r'C:\Users\USER\Downloads\FinalYearProject\data\advanced_agri_dataset.csv'
df.to_csv(output_path, index=False)
print(f"Successfully generated dataset with {len(df)} records at {output_path}")
