# Additional functions for chat.py - Part 1

new_functions = '''

def generate_pest_disease_advice(crop: str, question: str) -> str:
    """Generate pest/disease-specific advice."""
    advice = "## Pest & Disease Management\n\n"
    
    pest_keywords = {
        "stem borer": "Stem borer: Dead hearts, white heads. Control: Trichocards (Trichogramma), pheromone traps, resistant varieties, insecticides at economic threshold.",
        "brown planthopper": "BPH: Honeydew, sooty mold, hopperburn. Control: Resistant varieties, avoid excess N, alternate wetting/drying, buprofezin/dinotefuran if needed.",
        "leaf folder": "Leaf folder: Folded leaves, scraping. Control: Light traps, Trichogramma, chlorantraniliprole if severe.",
        "blast": "Rice blast: Diamond-shaped lesions. Control: Resistant varieties, balanced N, avoid excess water, tricyclazole/isoprothiolane.",
        "blight": "Bacterial leaf blight: Yellow stripes, wilting. Control: Resistant varieties, field sanitation, copper compounds, avoid injury.",
        "rust": "Rust: Orange/brown pustules. Control: Resistant varieties, early sowing, propiconazole/tebuconazole.",
        "bollworm": "Bollworm: Flared squares, damaged bolls. Control: Bt cotton, pheromone traps, Trichogramma, emamectin benzoate.",
        "aphid": "Aphids: Sticky leaves, curling. Control: Ladybird beetles, neem oil, imidacloprid if severe.",
        "whitefly": "Whitefly: Yellowing, sooty mold, virus vector. Control: Yellow sticky traps, neem, spiromesifen.",
        "termite": "Termites: Wilting, hollow stems. Control: Fipronil/chlorpyrifos seed treatment, neem cake, destroy mounds.",
        "nematode": "Nematodes: Stunted, yellowing, galled roots. Control: Crop rotation, marigold, carbofuran, solarization.",
    }
    
    matched = False
    for pest, control in pest_keywords.items():
        if pest in question:
            advice += f"**{pest.title()}**: {control}\n\n"
            matched = True
    
    if not matched:
        advice += "**General IPM (Integrated Pest Management) approach**:\n"
        advice += "1. **Monitor**: Regular field scouting, pheromone traps, yellow sticky traps\n"
        advice += "2. **Identify**: Correct pest/disease identification before action\n"
        advice += "3. **Threshold**: Apply chemicals only at Economic Threshold Level (ETL)\n"
        advice += "4. **Cultural**: Crop rotation, resistant varieties, timely sowing, field sanitation\n"
        advice += "5. **Biological**: Conserve natural enemies, release Trichogramma, NPV, Bacillus thuringiensis\n"
        advice += "6. **Chemical**: Last resort. Rotate modes of action. Follow PHI (pre-harvest interval)\n\n"
        
        if crop:
            crop_pests = {
                "rice": "Common: Stem borer, BPH, leaf folder, blast, blight, tungro",
                "wheat": "Common: Rust (yellow/brown/black), aphids, termites, loose smut",
                "cotton": "Common: Bollworm, aphid, whitefly, jassid, leaf curl virus",
                "sugarcane": "Common: Early shoot borer, top borer, pyrilla, red rot, wilt",
                "maize": "Common: Stem borer, fall armyworm, downy mildew, leaf blight",
                "pulses": "Common: Pod borer, aphid, wilt, yellow mosaic virus",
            }
            if crop in crop_pests:
                advice += f"**{crop.title()} specific**: {crop_pests[crop]}\n\n"
    
    advice += "**Safety**: Always read label. Wear PPE. Observe PHI. Don't spray during flowering (bee safety).\n"
    
    return advice
'''

print('Part 1 ready')