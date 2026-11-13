def generate_irrigation_schedule(crop: str, district: str, state: str, soil_type: str,
                                  planned_start_date, planting_season: str,
                                  land_area_ha: float) -> str:
    """Generate a detailed week-by-week irrigation schedule for the crop."""
    from datetime import date, timedelta

    if planned_start_date is None:
        if planting_season == 'Kharif':
            planned_start_date = date(date.today().year, 6, 15)
        elif planting_season == 'Rabi':
            planned_start_date = date(date.today().year, 10, 15)
        else:
            planned_start_date = date(date.today().year, 3, 1)

    crop_lower = crop.lower()
    
    irrigation_schedules = {
        'rice': {
            'Week 1 (Sowing)': 'Light irrigation for puddling and transplanting; maintain 2-3 cm water',
            'Week 2-3 (Establishment)': 'Maintain 3-5 cm standing water; daily if no rain',
            'Week 4-6 (Tillering)': 'Continuous 5 cm water; critical for tiller formation',
            'Week 7-10 (Panicle Initiation)': 'MAINTAIN 5 cm water - NO STRESS; most critical period',
            'Week 11-14 (Flowering)': 'MAINTAIN 5 cm water - NO STRESS; grain set depends on this',
            'Week 15-17 (Grain Filling)': 'Maintain 3-5 cm; gradually reduce in last week',
            'Week 18 (Maturity)': 'Stop irrigation 10-15 days before harvest; drain field',
        },
        'wheat': {
            'Week 1 (Sowing)': 'Pre-sowing irrigation (palewa) if soil dry; light irrigation after sowing',
            'Week 2-3 (Germination)': 'Light irrigation at 3-4 leaf stage; ensure good emergence',
            'Week 4-6 (Tillering)': '1st irrigation at CRI stage (21 DAS); critical for tillers',
            'Week 7-9 (Jointing)': '2nd irrigation at jointing; avoid water stress',
            'Week 10-11 (Booting)': '3rd irrigation at booting; flag leaf protection',
            'Week 12-13 (Flowering)': '4th irrigation at flowering; MOST CRITICAL',
            'Week 14-15 (Grain Filling)': '5th irrigation at milk stage; 6th at dough stage if needed',
            'Week 16 (Maturity)': 'Stop irrigation at hard dough stage; harvest at 12-14% moisture',
        },
        'maize': {
            'Week 1 (Sowing)': 'Light irrigation after sowing if no rain; ensure seed zone moisture',
            'Week 2-3 (Germination)': 'Irrigate if no rain >7 days; critical for uniform stand',
            'Week 4-6 (Vegetative V6-V12)': 'Irrigate at knee-high stage; earthing up after irrigation',
            'Week 7-9 (Tasseling/Silking)': 'CRITICAL - irrigate at tasseling and silking; no stress',
            'Week 10-13 (Grain Filling)': 'Regular irrigation every 7-10 days; avoid waterlogging',
            'Week 14 (Maturity)': 'Stop irrigation at physiological maturity (black layer)',
        },
        'cotton': {
            'Week 1 (Sowing)': 'Pre-sowing irrigation if dry; light irrigation after sowing',
            'Week 2-4 (Germination/Early)': 'Irrigate at 2-3 leaf stage; gap filling if needed',
            'Week 5-10 (Vegetative)': 'Irrigate at square formation; every 10-12 days',
            'Week 11-15 (Flowering)': 'CRITICAL - weekly irrigation during peak flowering',
            'Week 16-21 (Boll Development)': 'Regular irrigation every 10-12 days; avoid stress',
            'Week 22-24 (Boll Opening)': 'Reduce irrigation; stop 2-3 weeks before first picking',
        },
        'soybean': {
            'Week 1 (Sowing)': 'Pre-sowing irrigation if needed; light after sowing',
            'Week 2-3 (Germination)': 'Irrigate if dry >5 days; ensure emergence',
            'Week 4-6 (Vegetative)': 'Irrigate at branching stage; weed control after irrigation',
            'Week 7-10 (Flowering/Pod Formation)': 'CRITICAL - irrigate at flowering and pod set',
            'Week 11-13 (Seed Filling)': 'Regular irrigation every 10-12 days; pod filling critical',
            'Week 14-15 (Maturity)': 'Stop irrigation at yellow pod stage; harvest at 12-14% moisture',
        },
        'groundnut': {
            'Week 1 (Sowing)': 'Pre-sowing irrigation if dry; light irrigation after sowing for germination',
            'Week 2-3 (Germination)': 'Irrigate if dry >5 days; ensure uniform emergence',
            'Week 4-6 (Early Vegetative)': 'Irrigate at 3-4 leaf stage; critical for root development',
            'Week 7-10 (Pegging/Pod Formation)': 'CRITICAL - weekly irrigation during pegging; gypsum application',
            'Week 11-14 (Pod Development)': 'Regular irrigation every 7-10 days; avoid waterlogging',
            'Week 15-16 (Maturity)': 'Stop irrigation at yellow leaf stage; harvest at 12-14% moisture',
        },
        'sugarcane': {
            'Week 1-3 (Planting/Germination)': 'Heavy pre-plant irrigation; light frequent irrigation for germination',
            'Week 4-8 (Tillering)': 'Irrigate every 7-10 days; critical for tiller formation',
            'Week 9-20 (Grand Growth)': 'Irrigate every 7-10 days; MAXIMUM water demand period',
            'Week 21-30 (Maturity)': 'Irrigate every 10-15 days; reduce gradually',
            'Week 31-35 (Ripening)': 'Stop irrigation 3-4 weeks before harvest; increase sucrose',
        },
        'chickpea': {
            'Week 1 (Sowing)': 'Pre-sowing irrigation (palewa) if soil dry; light after sowing',
            'Week 2-3 (Germination)': 'Irrigate if dry >7 days; ensure emergence',
            'Week 4-6 (Vegetative)': 'Irrigate at branching stage (30 DAS); avoid excess water',
            'Week 7-10 (Flowering)': 'CRITICAL - irrigate at 50% flowering; no stress',
            'Week 11-14 (Pod Formation/Filling)': 'Irrigate at pod formation; one more at seed filling if dry',
            'Week 15-16 (Maturity)': 'Stop irrigation at pod maturity; harvest at 12-14% moisture',
        },
    }

    schedule = irrigation_schedules.get(crop_lower, irrigation_schedules['rice'])

    lines = []
    lines.append(f"# {crop.title()} Irrigation Schedule")
    lines.append(f"**Location**: {district}, {state} | **Soil**: {soil_type} | **Season**: {planting_season}")
    lines.append(f"**Planned Start**: {planned_start_date.strftime('%d %b %Y')} | **Area**: {land_area_ha} ha")
    lines.append("")
    
    soil_notes = {
        'sandy': '**Sandy Soil**: Increase frequency by 30-50%; reduce amount per irrigation',
        'clay': '**Clay Soil**: Longer intervals; avoid waterlogging; ensure drainage',
        'loam': '**Loam Soil**: Standard schedule works well; monitor moisture',
        'clay loam': '**Clay Loam**: Standard schedule; good water retention',
        'sandy loam': '**Sandy Loam**: Slightly more frequent; less water per application',
        'black': '**Black Cotton Soil**: Deep cracking; irrigate before cracks form',
        'red': '**Red Soil**: Low retention; frequent light irrigations',
        'laterite': '**Laterite**: Low retention; frequent light irrigations',
    }
    soil_key = soil_type.lower()
    for k, v in soil_notes.items():
        if k in soil_key:
            lines.append(v)
            lines.append("")

    for week, advice in schedule.items():
        week_date = planned_start_date + timedelta(weeks=list(schedule.keys()).index(week))
        lines.append(f"## {week} (Week of {week_date.strftime('%d %b %Y')})")
        lines.append(f"   {advice}")
        lines.append("")

    lines.append("---")
    lines.append("## Key Irrigation Principles")
    lines.append("")
    lines.append("| Principle | Guidance |")
    lines.append("|-----------|----------|")
    lines.append("| **Timing** | Irrigate early morning or late evening to reduce evaporation |")
    lines.append("| **Method** | Drip/sprinkler saves 30-50% water vs flood irrigation |")
    lines.append("| **Monitoring** | Check soil moisture at 15-30 cm depth; irrigate at 50% depletion |")
    lines.append("| **Critical Stages** | Never stress crop at flowering/grain filling/pod formation |")
    lines.append("| **Water Quality** | Test EC & pH; avoid saline water (>2 dS/m) for sensitive crops |")
    lines.append("")
    lines.append("*Note: Adjust based on rainfall, actual soil moisture, and local weather. Consult local KVK for precision scheduling.*")

    return "\n".join(lines)


def generate_fertilizer_plan(crop: str, district: str, state: str, soil_type: str,
                              planned_start_date, planting_season: str,
                              land_area_ha: float) -> str:
    """Generate a comprehensive fertilizer management plan."""
    from datetime import date, timedelta

    if planned_start_date is None:
        if planting_season == 'Kharif':
            planned_start_date = date(date.today().year, 6, 15)
        elif planting_season == 'Rabi':
            planned_start_date = date(date.today().year, 10, 15)
        else:
            planned_start_date = date(date.today().year, 3, 1)

    crop_lower = crop.lower()
    
    fertilizer_plans = {
        'rice': {
            'nutrient_needs': {'N': 120, 'P2O5': 60, 'K2O': 40},
            'basal': {'Urea': 65, 'DAP': 130, 'MOP': 67},
            'top_dressing': [
                {'stage': 'Tillering (21-25 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 65, 'note': '1st top dressing - 50% N'},
                {'stage': 'Panicle Initiation (45-50 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 65, 'note': '2nd top dressing - 50% N'},
            ],
            'organic': 'FYM 10-15 t/ha or compost 5 t/ha at land preparation; Azotobacter + PSB seed treatment',
            'biofertilizer': 'Blue-green algae (BGA) 10 kg/ha at 7 DAS; Azolla 500 kg/ha as dual crop',
            'micronutrients': 'ZnSO4 25 kg/ha (if deficient); FeSO4 0.5% foliar spray at tillering',
        },
        'wheat': {
            'nutrient_needs': {'N': 120, 'P2O5': 60, 'K2O': 40},
            'basal': {'Urea': 65, 'DAP': 130, 'MOP': 67},
            'top_dressing': [
                {'stage': 'CRI Stage (21 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 65, 'note': '1st irrigation + 50% N'},
                {'stage': 'Jointing (45 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 65, 'note': '2nd irrigation + 50% N'},
            ],
            'organic': 'FYM 10-15 t/ha at land preparation; Azotobacter + PSB seed treatment',
            'biofertilizer': 'Azotobacter 5 kg/ha + PSB 5 kg/ha soil application',
            'micronutrients': 'ZnSO4 25 kg/ha (basal); FeSO4 0.5% foliar at jointing if deficient',
        },
        'maize': {
            'nutrient_needs': {'N': 150, 'P2O5': 75, 'K2O': 60},
            'basal': {'Urea': 55, 'DAP': 163, 'MOP': 100},
            'top_dressing': [
                {'stage': 'Knee-high / V6 (30 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 165, 'note': '1st top dressing - 75% N + earthing up'},
                {'stage': 'Tasseling (50 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 55, 'note': '2nd top dressing - 25% N (if needed)'},
            ],
            'organic': 'FYM 15 t/ha or vermicompost 5 t/ha; Azotobacter + PSB seed treatment',
            'biofertilizer': 'Azotobacter 5 kg/ha + PSB 5 kg/ha; blue-green algae in wet areas',
            'micronutrients': 'ZnSO4 25 kg/ha (basal); Borax 10 kg/ha if deficient',
        },
        'cotton': {
            'nutrient_needs': {'N': 120, 'P2O5': 60, 'K2O': 60},
            'basal': {'Urea': 33, 'DAP': 130, 'MOP': 100},
            'top_dressing': [
                {'stage': 'Square Formation (45 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 87, 'note': '1st top dressing - 50% N'},
                {'stage': 'Peak Flowering (75 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 87, 'note': '2nd top dressing - 50% N'},
            ],
            'organic': 'FYM 12-15 t/ha; vermicompost 3-5 t/ha; cotton stalk compost',
            'biofertilizer': 'Azotobacter + PSB + KSB (potash solubilizing) each 5 kg/ha',
            'micronutrients': 'ZnSO4 25 kg/ha; MgSO4 20 kg/ha; Boron 0.2% foliar at flowering',
        },
        'soybean': {
            'nutrient_needs': {'N': 20, 'P2O5': 60, 'K2O': 40},
            'basal': {'Urea': 22, 'DAP': 130, 'MOP': 67},
            'top_dressing': [
                {'stage': 'Branching (30 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 22, 'note': 'Starter N only (20 kg/ha)'},
                {'stage': 'Pod Formation (50 DAS)', 'fertilizer': 'DAP', 'rate_kg_ha': 55, 'note': 'P boost for pod filling (optional)'},
            ],
            'organic': 'FYM 10 t/ha; Rhizobium + PSB seed treatment (CRITICAL for N fixation)',
            'biofertilizer': 'Rhizobium japonicum + PSB seed treatment; Trichoderma for disease',
            'micronutrients': 'Gypsum 200-250 kg/ha (Ca + S); Borax 10 kg/ha; Mo seed treatment',
        },
        'groundnut': {
            'nutrient_needs': {'N': 20, 'P2O5': 40, 'K2O': 40},
            'basal': {'Urea': 22, 'DAP': 87, 'MOP': 67},
            'top_dressing': [
                {'stage': 'Pegging (35 DAS)', 'fertilizer': 'Gypsum', 'rate_kg_ha': 250, 'note': 'Ca for pod development - CRITICAL'},
            ],
            'organic': 'FYM 10 t/ha; Rhizobium + PSB seed treatment',
            'biofertilizer': 'Rhizobium (groundnut strain) + PSB; blue-green algae',
            'micronutrients': 'Gypsum 250 kg/ha at pegging; Borax 10 kg/ha basal',
        },
        'sugarcane': {
            'nutrient_needs': {'N': 250, 'P2O5': 115, 'K2O': 115},
            'basal': {'Urea': 55, 'DAP': 250, 'MOP': 192},
            'top_dressing': [
                {'stage': 'Tillering (45 DAP)', 'fertilizer': 'Urea', 'rate_kg_ha': 165, 'note': '1st top dressing'},
                {'stage': 'Grand Growth (90 DAP)', 'fertilizer': 'Urea', 'rate_kg_ha': 165, 'note': '2nd top dressing'},
                {'stage': 'Maturity (150 DAP)', 'fertilizer': 'Urea', 'rate_kg_ha': 110, 'note': '3rd top dressing (if ratoon)'},
            ],
            'organic': 'FYM 25-30 t/ha; pressmud 10-15 t/ha; trash mulching',
            'biofertilizer': 'Azotobacter + Acetobacter + PSB + KSB each 5 kg/ha',
            'micronutrients': 'ZnSO4 25 kg/ha; FeSO4 foliar 0.5% at 45 & 75 DAP',
        },
        'chickpea': {
            'nutrient_needs': {'N': 20, 'P2O5': 50, 'K2O': 30},
            'basal': {'Urea': 22, 'DAP': 109, 'MOP': 50},
            'top_dressing': [
                {'stage': 'Branching (30 DAS)', 'fertilizer': 'Urea', 'rate_kg_ha': 22, 'note': 'Starter N only'},
            ],
            'organic': 'FYM 10 t/ha; Rhizobium + PSB seed treatment',
            'biofertilizer': 'Rhizobium (chickpea strain) + PSB; Trichoderma viride 4 g/kg seed',
            'micronutrients': 'ZnSO4 25 kg/ha if deficient; FeSO4 foliar if chlorosis',
        },
    }
    plan = fertilizer_plans.get(crop_lower, fertilizer_plans['rice'])

    lines = []
    lines.append(f"# {crop.title()} Fertilizer Management Plan")
    lines.append(f"**Location**: {district}, {state} | **Soil**: {soil_type} | **Season**: {planting_season}")
    lines.append(f"**Planned Start**: {planned_start_date.strftime('%d %b %Y')} | **Area**: {land_area_ha} ha")
    lines.append("")
    lines.append("## Target Nutrient Requirement (kg/ha)")
    lines.append("")
    lines.append("| Nutrient | Requirement (kg/ha) |")
    lines.append("|----------|---------------------|")
    for nut, val in plan['nutrient_needs'].items():
        lines.append(f"| {nut} | {val} |")
    lines.append("")
    lines.append("## Basal Dose (At Sowing/Transplanting)")
    lines.append("")
    lines.append("| Fertilizer | Rate (kg/ha) | Nutrient Supplied |")
    lines.append("|------------|--------------|-------------------|")
    for fert, rate in plan['basal'].items():
        if fert == 'Urea':
            lines.append(f"| {fert} (46% N) | {rate} | N: {rate * 0.46:.0f} kg |")
        elif fert == 'DAP':
            lines.append(f"| {fert} (18% N, 46% P2O5) | {rate} | N: {rate * 0.18:.0f}, P2O5: {rate * 0.46:.0f} kg |")
        elif fert == 'MOP':
            lines.append(f"| {fert} (60% K2O) | {rate} | K2O: {rate * 0.60:.0f} kg |")
        else:
            lines.append(f"| {fert} | {rate} | - |")
    lines.append("")
    lines.append("## Top Dressing Schedule")
    lines.append("")
    lines.append("| Stage (DAS) | Fertilizer | Rate (kg/ha) | Note |")
    lines.append("|-------------|------------|--------------|------|")
    for td in plan['top_dressing']:
        stage = td['stage']
        fert = td['fertilizer']
        rate = td['rate_kg_ha']
        note = td['note']
        lines.append(f"| {stage} | {fert} | {rate} | {note} |")
    lines.append("")
    lines.append("## Organic & Biofertilizer Recommendations")
    lines.append("")
    lines.append(f"**Organic Manure**: {plan['organic']}")
    lines.append("")
    lines.append(f"**Biofertilizers**: {plan['biofertilizer']}")
    lines.append("")
    lines.append("## Micronutrient Management")
    lines.append("")
    lines.append(plan['micronutrients'])
    lines.append("")
    lines.append("## Soil-Specific Adjustments")
    lines.append("")
    soil_adjustments = {
        'sandy': '- **Sandy Soil**: Split N into 3-4 doses; increase K by 20%; add S (gypsum/elemental S)',
        'clay': '- **Clay Soil**: Standard splits; avoid N loss by deep placement; ensure drainage',
        'loam': '- **Loam Soil**: Standard recommendation works well',
        'clay loam': '- **Clay Loam**: Standard; good nutrient retention',
        'sandy loam': '- **Sandy Loam**: Extra N split; monitor K leaching',
        'black': '- **Black Cotton Soil**: High K reserve; reduce K2O by 25%; add S, Zn',
        'red': '- **Red Soil**: Acidic; lime @ 2-3 t/ha if pH<5.5; increase P availability',
        'laterite': '- **Laterite**: Very acidic; lime essential; high P fixation - use rock phosphate',
    }
    soil_key = soil_type.lower()
    for k, v in soil_adjustments.items():
        if k in soil_key:
            lines.append(v)
            lines.append("")
    lines.append("---")
    lines.append("## Best Practices")
    lines.append("")
    lines.append("| Practice | Details |")
    lines.append("|----------|---------|")
    lines.append("| **Soil Test** | Always base plan on recent soil test (<=2 years) |")
    lines.append("| **4R Nutrient Stewardship** | Right Source, Right Rate, Right Time, Right Place |")
    lines.append("| **Incorporation** | Mix basal fertilizers 10-15 cm deep; avoid surface broadcasting |")
    lines.append("| **Split N** | Never apply all N at once; 3-4 splits for most crops |")
    lines.append("| **Placement** | Band placement 5 cm beside & below seed; top dress near root zone |")
    lines.append("| **Foliar** | 0.5-1% urea or 19:19:19 at critical stages for quick uptake |")
    lines.append("| **Record Keeping** | Maintain fertilizer register for each field/season |")
    lines.append("")
    lines.append("*Note: These are general guidelines. Adjust based on soil test, variety, yield target, and local KVK/SAU recommendations.*")

    return "\n".join(lines)
