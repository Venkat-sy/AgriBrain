# Additional functions for chat.py - Part 2

new_functions_2 = '''

def generate_harvest_advice(crop: str) -> str:
    """Generate harvest-specific advice."""
    advice = "## Harvest & Post-Harvest Management\n\n"
    
    crop_harvest = {
        "rice": "Harvest at 20-25% grain moisture (80-85% grains straw-colored). Thresh within 24h. Dry to 12-14% for storage. Yield loss 5-10% if delayed.",
        "wheat": "Harvest at 18-20% moisture (grains hard, straw golden). Combine harvest preferred. Dry to 12% for storage. Avoid rain at harvest.",
        "cotton": "Pick at fully open bolls (3-4 pickings). Morning picking for quality. Grade separately. Store dry, ventilated.",
        "sugarcane": "Harvest at 10-12 months (brix >18%). Cut at ground level. Crush within 24h. Avoid burning.",
        "maize": "Harvest at 20-25% kernel moisture (black layer formed). Shell at 15% moisture. Dry to 13% for storage.",
        "pulses": "Harvest when 80% pods brown (shattering risk). Morning harvest. Dry to 10-12% moisture.",
        "groundnut": "Harvest when pods mature (inner shell dark). Dry in windrows 2-3 days. Strip pods. Dry to 8-10%.",
        "mustard": "Harvest when 75% pods yellow-brown. Morning to avoid shattering. Dry to 8-9% moisture.",
    }
    
    if crop in crop_harvest:
        advice += f"**{crop.title()}**: {crop_harvest[crop]}\n\n"
    else:
        advice += "**General**: Harvest at physiological maturity. Use proper tools. Minimize damage. Dry properly before storage.\n\n"
    
    advice += "**Post-harvest checklist**:\n"
    advice += "• Clean produce (remove debris, damaged grains)\n"
    advice += "• Dry to safe moisture level (cereals 12-14%, pulses 10-12%, oilseeds 8-9%)\n"
    advice += "• Grade and sort for better price\n"
    advice += "• Store in clean, dry, ventilated structures\n"
    advice += "• Use hermetic bags or metal bins for long storage\n"
    advice += "• Treat storage structure (malathion spray, aluminum phosphide fumigation if needed)\n"
    advice += "• Monitor regularly for pests, moisture, temperature\n"
    
    return advice


def generate_soil_advice(soil_type: str, crop: str) -> str:
    """Generate soil-specific advice."""
    advice = "## Soil Health & Management\n\n"
    
    if soil_type:
        soil_info = {
            "sandy": "Sandy soil: Low water/nutrient retention. Add organic matter (FYM/compost 10-15 t/ha). Frequent light irrigation. Green manuring. Mulch heavily.",
            "clay": "Clay soil: High retention but poor drainage/aeration. Add gypsum (2-5 t/ha) for sodic clay. Organic matter improves structure. Avoid compaction. Raised beds.",
            "loam": "Loam soil: Ideal for most crops. Maintain with regular organic matter. Balanced fertilization. Good drainage and aeration.",
            "black": "Black cotton soil: High shrink-swell. Crack management. Deep plowing in summer. Gypsum if sodic. Wide-spaced crops. Avoid waterlogging.",
            "red": "Red soil: Acidic, low CEC. Lime (2-4 t/ha) if pH <5.5. High P fixation - band placement. Organic matter critical. Micronutrient deficiencies common.",
            "laterite": "Laterite: Highly acidic, low fertility. Heavy liming. High organic matter. Split fertilizers. Acid-tolerant crops (cashew, mango, tea).",
            "alluvial": "Alluvial: Fertile, young soils. Good response to fertilizers. Watch for micronutrient depletion over time. Regular soil testing.",
            "desert": "Desert soil: Sandy, alkaline, low organic matter. Windbreaks. Drip irrigation. Salt-tolerant crops. Heavy organic amendments.",
            "peat": "Peaty soil: High organic, acidic. Drainage needed. Liming. Suitable for rice, vegetables after improvement.",
        }
        for key, val in soil_info.items():
            if key in soil_type:
                advice += f"**{soil_type.title()} soil**: {val}\n\n"
                break
    
    if crop:
        crop_soil = {
            "rice": "Prefers clay/clay loam, pH 5.5-6.5, puddled conditions. Tolerates flooding.",
            "wheat": "Prefers loam/clay loam, pH 6.0-7.5, well-drained. Sensitive to salinity.",
            "cotton": "Prefers deep black/loam, pH 5.8-8.0, well-drained. Sensitive to waterlogging.",
            "sugarcane": "Prefers deep loam/clay loam, pH 6.0-7.5, good drainage. High nutrient demand.",
            "maize": "Prefers well-drained loam, pH 5.5-7.0. Sensitive to waterlogging and acidity.",
            "pulses": "Prefers well-drained loam, pH 6.0-7.5. Rhizobium needs neutral pH. Sensitive to salinity.",
        }
        if crop in crop_soil:
            advice += f"**{crop.title()} soil preference**: {crop_soil[crop]}\n\n"
    
    advice += "**Universal soil health practices**:\n"
    advice += "• Test soil every 2-3 years (pH, EC, OC, NPK, micros)\n"
    advice += "• Maintain organic carbon >0.5% (ideally 0.75-1%)\n"
    advice += "• Practice crop rotation (cereal-legume-oilseed)\n"
    advice += "• Green manuring (dhaincha, sunhemp, sesbania)\n"
    advice += "• Conservation agriculture: minimum till, residue retention, rotation\n"
    advice += "• Biochar for long-term carbon sequestration\n"
    advice += "• Balanced fertilization based on soil test (STCR approach)\n"
    
    return advice
'''

print('Part 2 ready')