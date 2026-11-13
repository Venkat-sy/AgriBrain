#!/usr/bin/env python
"""
Manual corrections for ICRISAT district names.
"""
MANUAL_CORRECTIONS = {
    # Madhya Pradesh - name changes
    ('NARSINGHPUR', 'MADHYA PRADESH'): ('Narsimhapur', 'Madhya Pradesh'),
    ('SEONI / SHIVANI', 'MADHYA PRADESH'): ('Seoni', 'Madhya Pradesh'),
    ('KHARGONE / WEST NIMAR', 'MADHYA PRADESH'): ('West Nimar', 'Madhya Pradesh'),
    ('KHANDWA / EAST NIMAR', 'MADHYA PRADESH'): ('East Nimar', 'Madhya Pradesh'),
    ('KHARGONE / WEST NIMAR', 'MADHYA PRADESH'): ('West Nimar', 'Madhya Pradesh'),
    ('KHANDWA / EAST NIMAR', 'MADHYA PRADESH'): ('East Nimar', 'Madhya Pradesh'),
    ('SEONI / SHIVANI', 'MADHYA PRADESH'): ('Seoni', 'Madhya Pradesh'),
    ('NARSINGHPUR', 'MADHYA PRADESH'): ('Narsimhapur', 'Madhya Pradesh'),
    
    # Andhra Pradesh - name changes (includes pre-2014 Telangana districts)
    ('S.P.S. NELLORE', 'ANDHRA PRADESH'): ('Sri Potti Sriramulu Nellore', 'Andhra Pradesh'),
    ('ANANTHAPUR', 'ANDHRA PRADESH'): ('Anantapur', 'Andhra Pradesh'),
    ('KADAPA YSR', 'ANDHRA PRADESH'): ('Y.s.r.', 'Andhra Pradesh'),
    
    # Telangana - map to Andhra Pradesh canonical names (GeoJSON uses combined state)
    ('HYDERABAD', 'TELANGANA'): ('Hyderabad', 'Andhra Pradesh'),
    ('NIZAMABAD', 'TELANGANA'): ('Nizamabad', 'Andhra Pradesh'),
    ('MEDAK', 'TELANGANA'): ('Medak', 'Andhra Pradesh'),
    ('MAHABUBNAGAR', 'TELANGANA'): ('Mahbubnagar', 'Andhra Pradesh'),
    ('NALGONDA', 'TELANGANA'): ('Nalgonda', 'Andhra Pradesh'),
    ('WARANGAL', 'TELANGANA'): ('Warangal', 'Andhra Pradesh'),
    ('KHAMMAM', 'TELANGANA'): ('Khammam', 'Andhra Pradesh'),
    ('KARIMNAGAR', 'TELANGANA'): ('Karimnagar', 'Andhra Pradesh'),
    ('ADILABAD', 'TELANGANA'): ('Adilabad', 'Andhra Pradesh'),
    
    # Karnataka - name changes (GeoJSON uses old names)
    ('SHIMOGUE', 'KARNATAKA'): ('Shimoga', 'Karnataka'),
    ('SHIMOGUE', 'KARNATAKA'): ('Shimoga', 'Karnataka'),
    ('SHIMOGUE', 'KARNATAKA'): ('Shimoga', 'Karnataka'),
    ('SHIMOGE', 'KARNATAKA'): ('Shimoga', 'Karnataka'),
    ('CHICKMAGALUR', 'KARNATAKA'): ('Chikmagalur', 'Karnataka'),
    ('BIJAPUR / VIJAYAPURA', 'KARNATAKA'): ('Bijapur', 'Karnataka'),
    ('GULBARGA / KALABURAGI', 'KARNATAKA'): ('Gulbarga', 'Karnataka'),
    ('KODAGU / COORG', 'KARNATAKA'): ('Kodagu', 'Karnataka'),
    
    # Tamil Nadu - name changes
    ('CHENGALPATTU MGR / KANCHIPURAM', 'TAMIL NADU'): ('Kancheepuram', 'Tamil Nadu'),
    ('SOUTH ARCOT / CUDDALORE', 'TAMIL NADU'): ('Cuddalore', 'Tamil Nadu'),
    ('NORTH ARCOT / VELLORE', 'TAMIL NADU'): ('Vellore', 'Tamil Nadu'),
    ('TIRUCHIRAPALLI / TRICHY', 'TAMIL NADU'): ('Tiruchirappalli', 'Tamil Nadu'),
    ('RAMANANTHAPURAM', 'TAMIL NADU'): ('Ramanathapuram', 'Tamil Nadu'),
    ('THIRUNELVELI', 'TAMIL NADU'): ('Tirunelveli', 'Tamil Nadu'),
    ('KANYAKUMARI', 'TAMIL NADU'): ('Kanniyakumari', 'Tamil Nadu'),
    
    # Maharashtra
    ('BOMBAY', 'MAHARASHTRA'): ('Mumbai', 'Maharashtra'),
    ('RAIGAD', 'MAHARASHTRA'): ('Raigarh', 'Maharashtra'),
    ('NASIK', 'MAHARASHTRA'): ('Nashik', 'Maharashtra'),
    ('AHMEDNAGAR', 'MAHARASHTRA'): ('Ahmadnagar', 'Maharashtra'),
    ('BEED', 'MAHARASHTRA'): ('Bid', 'Maharashtra'),
    ('BULDHANA', 'MAHARASHTRA'): ('Buldana', 'Maharashtra'),
    ('AMARAWATI', 'MAHARASHTRA'): ('Amravati', 'Maharashtra'),
    ('YEOTMAL', 'MAHARASHTRA'): ('Yavatmal', 'Maharashtra'),
    
    # Gujarat - GeoJSON uses different names
    ('AHMEDABAD', 'GUJARAT'): ('Ahmadabad', 'Gujarat'),
    ('BANASKANTHA', 'GUJARAT'): ('Banas Kantha', 'Gujarat'),
    ('VADODARA / BARODA', 'GUJARAT'): ('Vadodara', 'Gujarat'),
    ('MEHSANA', 'GUJARAT'): ('Mahesana', 'Gujarat'),
    ('PANCHMAHAL', 'GUJARAT'): ('Panch Mahals', 'Gujarat'),
    ('SABARKANTHA', 'GUJARAT'): ('Sabar Kantha', 'Gujarat'),
    ('KUTCH', 'GUJARAT'): ('Kachchh', 'Gujarat'),
    
    # Rajasthan
    ('CHITTORGARH', 'RAJASTHAN'): ('Chittaurgarh', 'Rajasthan'),
    ('JALORE', 'RAJASTHAN'): ('Jalor', 'Rajasthan'),
    ('SWAMI MADHOPUR', 'RAJASTHAN'): ('Sawai Madhopur', 'Rajasthan'),
    
    # Punjab
    ('ROOPNAGAR / ROPAR', 'PUNJAB'): ('Rupnagar', 'Punjab'),
    ('FEROZPUR', 'PUNJAB'): ('Firozpur', 'Punjab'),
    ('BHATINDA', 'PUNJAB'): ('Bathinda', 'Punjab'),
    
    # Haryana
    ('HISSAR', 'HARYANA'): ('Hisar', 'Haryana'),
    ('MAHENDRAGARH / NARNAUL', 'HARYANA'): ('Mahendragarh', 'Haryana'),
    
    # Uttar Pradesh
    ('BULAND SHAHAR', 'UTTAR PRADESH'): ('Bulandshahr', 'Uttar Pradesh'),
    ('KANPUR', 'UTTAR PRADESH'): ('Kanpur Nagar', 'Uttar Pradesh'),
    ('MIRZPUR', 'UTTAR PRADESH'): ('Mirzapur', 'Uttar Pradesh'),
    ('RAE-BAREILY', 'UTTAR PRADESH'): ('Rae Bareli', 'Uttar Pradesh'),
    ('BARABANKI', 'UTTAR PRADESH'): ('Bara Banki', 'Uttar Pradesh'),
    
    # Uttarakhand
    ('ALMORAH', 'UTTARAKHAND'): ('Almora', 'Uttarakhand'),
    ('PITHORGARH', 'UTTARAKHAND'): ('Pithoragarh', 'Uttarakhand'),
    ('UTTAR KASHI', 'UTTARAKHAND'): ('Uttarkashi', 'Uttarakhand'),
    
    # Assam
    ('NORTH CACHAR HIL / DIMA HASAO', 'ASSAM'): ('Dima Hasao', 'Assam'),
    ('SIBSAGAR', 'ASSAM'): ('Sivasagar', 'Assam'),
    
    # Himachal Pradesh
    ('BILASHPUR', 'HIMACHAL PRADESH'): ('Bilaspur', 'Himachal Pradesh'),
    
    # Kerala
    ('ERANAKULAM', 'KERALA'): ('Ernakulam', 'Kerala'),
    
    # Odisha
    ('BALASORE', 'ORISSA'): ('Baleshwar', 'Odisha'),
    ('BOLANGIR', 'ORISSA'): ('Balangir', 'Odisha'),
    ('CUTTACK', 'ORISSA'): ('Cuttack', 'Odisha'),
    ('DHENKANAL', 'ORISSA'): ('Dhenkanal', 'Odisha'),
    ('GANJAM', 'ORISSA'): ('Ganjam', 'Odisha'),
    ('KALAHANDI', 'ORISSA'): ('Kalahandi', 'Odisha'),
    ('KEONJHAR', 'ORISSA'): ('Kendujhar', 'Odisha'),
    ('KORAPUT', 'ORISSA'): ('Koraput', 'Odisha'),
    ('MAYURBHANJA', 'ORISSA'): ('Mayurbhanj', 'Odisha'),
    ('PHULBANI ( KANDHAMAL )', 'ORISSA'): ('Kandhamal', 'Odisha'),
    ('PURI', 'ORISSA'): ('Puri', 'Odisha'),
    ('SAMBALPUR', 'ORISSA'): ('Sambalpur', 'Odisha'),
    ('SUNDARGARH', 'ORISSA'): ('Sundargarh', 'Odisha'),
    
    # West Bengal
    ('24 PARGANAS', 'WEST BENGAL'): ('North 24 Parganas', 'West Bengal'),
    ('BURDWAN', 'WEST BENGAL'): ('Barddhaman', 'West Bengal'),
    ('HOOGHLY', 'WEST BENGAL'): ('Hugli', 'West Bengal'),
    ('HOWRAH', 'WEST BENGAL'): ('Haora', 'West Bengal'),
    ('DARJEELING', 'WEST BENGAL'): ('Darjiling', 'West Bengal'),
    ('COOCH BEHAR', 'WEST BENGAL'): ('Koch Bihar', 'West Bengal'),
    ('PURULIA', 'WEST BENGAL'): ('Puruliya', 'West Bengal'),
    ('MIDNAPUR', 'WEST BENGAL'): ('Pashchim Medinipur', 'West Bengal'),
    ('WEST DINAJPUR', 'WEST BENGAL'): ('Uttar Dinajpur', 'West Bengal'),
    
    # Bihar
    ('CHAMPARAN', 'BIHAR'): ('Pashchim Champaran', 'Bihar'),
    ('PURNEA', 'BIHAR'): ('Purnia', 'Bihar'),
    ('MUNGAIR', 'BIHAR'): ('Munger', 'Bihar'),
    
    # Jharkhand
    ('SANTHAL PARAGANA / DUMKA', 'JHARKHAND'): ('Dumka', 'Jharkhand'),
    ('SHAHABAD (NOW PART OF BHOJPUR DISTRICT)', 'BIHAR'): ('Bhojpur', 'Bihar'),
    ('PALAMAU', 'JHARKHAND'): ('Palamu', 'Jharkhand'),
    ('SINGHBHUM', 'JHARKHAND'): ('Purbi Singhbhum', 'Jharkhand'),
}