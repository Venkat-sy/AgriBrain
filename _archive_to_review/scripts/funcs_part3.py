# Additional functions for chat.py - Part 3

new_functions_3 = '''

def generate_weather_advice(crop: str, district: str) -> str:
    """Generate weather/climate-specific advice."""
    advice = "## Weather & Climate Smart Agriculture\n\n"
    
    advice += "**Monsoon preparedness**:\n"
    advice += "• Pre-monsoon: Land preparation, seed procurement, drainage cleaning\n"
    advice += "• Early monsoon: Timely sowing, weed management, basal fertilizer\n"
    advice += "• Mid-monsoon: Top dressing, pest monitoring, water management\n"
    advice += "• Late monsoon: Disease management, harvest planning\n"
    advice += "• Post-monsoon: Rabi sowing, soil moisture conservation\n\n"
    
    advice += "**Extreme weather management**:\n"
    advice += "• **Drought**: Drought-tolerant varieties, mulching, drip irrigation, antitranspirants, life-saving irrigation\n"
    advice += "• **Flood/Waterlogging**: Drainage channels, raised beds, submergence-tolerant varieties (Swarna Sub1 for rice), post-flood N top-up\n"
    advice += "• **Heat wave**: Light irrigation, mulching, shade nets for vegetables, avoid spraying at peak heat\n"
    advice += "• **Cold wave/Frost**: Smoke/fogging, irrigation before frost, windbreaks, tolerant varieties\n"
    advice += "• **Hail**: Hail nets for high-value crops, prompt harvest if near maturity, fungicide after hail injury\n"
    advice += "• **Cyclone**: Early harvest if possible, propping/lodging prevention, drainage\n\n"
    
    if crop:
        climate_crop = {
            "rice": "Kharif rice: Sow with monsoon onset. Transplant 21-25 DAS. Avoid late transplanting (yield loss). Rabi rice needs assured irrigation.",
            "wheat": "Rabi wheat: Timely sow (Nov 1-15 ideal). Late sowing loses 1% yield/day. Heat stress at grain fill reduces yield.",
            "cotton": "Kharif cotton: Sow pre-monsoon (Apr-May) or with monsoon. Long duration. Avoid late sowing (pink bollworm risk).",
            "sugarcane": "Plant: Feb-Mar (spring) or Oct-Nov (autumn). Ratoon management critical. Waterlogging sensitive.",
            "maize": "Kharif: With monsoon. Rabi: Oct-Nov (needs irrigation). Spring: Jan-Feb (high yield with irrigation).",
            "pulses": "Kharif: Arhar, moong, urad with monsoon. Rabi: Chickpea, lentil, pea (Oct-Nov). Moisture conservation critical.",
        }
        if crop in climate_crop:
            advice += f"**{crop.title()} climate calendar**: {climate_crop[crop]}\n\n"
    
    advice += "**Climate information sources**:\n"
    advice += "• IMD (India Meteorological Department) - district forecasts\n"
    advice += "• Meghdoot app - crop-specific advisories\n"
    advice += "• Kisan Call Centre (1800-180-1551)\n"
    advice += "• State agricultural university KVKs\n"
    advice += "• Weather-based crop insurance (PMFBY)\n"
    
    return advice


def generate_general_advice(crop: str, district: str, soil_type: str) -> str:
    """Generate general farming advice."""
    advice = "## General Farming Advisory\n\n"
    
    if crop:
        advice += f"**Crop: {crop.title()}**\n"
        advice += f"For specific {crop} advice, ask about irrigation, fertilizer, pests, harvest, or soil management.\n\n"
    
    if district:
        advice += f"**Location: {district.title()}**\n"
        advice += "Consult local KVK (Krishi Vigyan Kendra) for district-specific varieties and practices.\n\n"
    
    if soil_type:
        advice += f"**Soil: {soil_type.title()}**\n"
        advice += "Get soil tested for precise fertilizer recommendations.\n\n"
    
    advice += "**Essential farming practices**:\n"
    advice += "1. **Planning**: Crop calendar, variety selection, input procurement\n"
    advice += "2. **Soil health**: Test, organic matter, balanced nutrition\n"
    advice += "3. **Seed**: Quality seed, treatment, correct rate/spacing\n"
    advice += "4. **Water**: Efficient irrigation, scheduling, conservation\n"
    advice += "5. **Protection**: IPM, monitoring, threshold-based decisions\n"
    advice += "6. **Harvest**: Timely, proper method, post-harvest care\n"
    advice += "7. **Marketing**: Grade, store, collective marketing, value addition\n"
    advice += "8. **Records**: Maintain field diary for learning & schemes\n\n"
    
    advice += "**Government schemes to explore**:\n"
    advice += "• PM-KISAN (income support)\n"
    advice += "• PMFBY (crop insurance)\n"
    advice += "• Soil Health Card\n"
    advice += "• PMKSY (irrigation)\n"
    advice += "• PKVY (organic farming)\n"
    advice += "• RKVY-RAFTAAR (infrastructure)\n"
    advice += "• State-specific schemes (check with local agriculture dept)\n\n"
    
    advice += "**Need specific help?** Ask me about:\n"
    advice += "• Irrigation schedule for your crop\n"
    advice += "• Fertilizer dose and timing\n"
    advice += "• Pest/disease identification and control\n"
    advice += "• Harvest timing and post-harvest handling\n"
    advice += "• Soil improvement for your soil type\n"
    advice += "• Weather-based decisions\n"
    advice += "• Variety selection for your region\n"
    
    return advice
'''

print('Part 3 ready')