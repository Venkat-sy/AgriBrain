#!/usr/bin/env python3
"""
Comprehensive database seeding script for AgriBrain.
Seeds: districts (150+ pan-India), soil_types, district_soil_types, crop_profiles, 
crop_costs, crop_prices, rainfall_monthly, rainfall_forecasts
Uses data from crops_master.yaml and adds realistic sample data.
"""

import sys
import os
import yaml
import random
import json
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.config import engine, get_settings
from backend.models import (
    District, SoilType, DistrictSoilType, CropProfile,
    CropCost, CropPrice, RainfallMonthly, RainfallForecast
)
from sqlalchemy.orm import Session
from sqlalchemy import select, func, text


def load_crops_master():
    """Load crops from crops_master.yaml."""
    yaml_path = Path(__file__).parent.parent / "data" / "crops_master.yaml"
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    return data["crops"]


def seed_districts(session: Session):
    """Seed 150+ districts across all 15 ICAR Agro-Climatic Zones."""
    print("Seeding districts (pan-India)...")
    
    existing_count = session.execute(select(func.count(District.id))).scalar()
    if existing_count > 10:
        print(f"  Already {existing_count} districts, skipping")
        return existing_count
    
    # Clear existing if only a few
    if existing_count > 0 and existing_count <= 10:
        session.execute(text("TRUNCATE TABLE district_soil_types RESTART IDENTITY CASCADE"))
        session.execute(text("TRUNCATE TABLE districts RESTART IDENTITY CASCADE"))
        session.commit()
    
    # 15 ICAR Agro-Climatic Zones with major districts
    # Each zone: list of (district_name, state, state_code, lat, lon, district_code, zone_name, soil_type)
    districts_data = [
        # Zone 1: Western Himalayan Temperate Zone
        ("Shimla", "Himachal Pradesh", "HP", 31.1048, 77.1734, "171", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Kullu", "Himachal Pradesh", "HP", 31.9572, 77.1098, "172", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Mandi", "Himachal Pradesh", "HP", 31.7092, 76.9323, "173", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Kangra", "Himachal Pradesh", "HP", 32.1008, 76.2701, "174", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Chamba", "Himachal Pradesh", "HP", 32.5538, 76.1292, "175", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Srinagar", "Jammu & Kashmir", "JK", 34.0837, 74.7973, "181", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Jammu", "Jammu & Kashmir", "JK", 32.7266, 74.8570, "182", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Anantnag", "Jammu & Kashmir", "JK", 33.7311, 75.1479, "183", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Leh", "Ladakh", "LA", 34.1526, 77.5770, "191", "Western Himalayan Temperate Zone", "Cold Desert Soil"),
        ("Kargil", "Ladakh", "LA", 34.5420, 76.1339, "192", "Western Himalayan Temperate Zone", "Cold Desert Soil"),
        ("Uttarkashi", "Uttarakhand", "UK", 30.7306, 78.4460, "201", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Chamoli", "Uttarakhand", "UK", 30.4131, 79.3287, "202", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Pithoragarh", "Uttarakhand", "UK", 29.5833, 80.2167, "203", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Almora", "Uttarakhand", "UK", 29.5971, 79.6591, "204", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        ("Nainital", "Uttarakhand", "UK", 29.3805, 79.4636, "205", "Western Himalayan Temperate Zone", "Mountain Forest / Podzolic Loam"),
        
        # Zone 2: Eastern Himalayan Zone
        ("Darjeeling", "West Bengal", "WB", 27.0380, 88.2636, "701", "Eastern Himalayan Zone", "Red & Lateritic Soil"),
        ("Kalimpong", "West Bengal", "WB", 27.0630, 88.4730, "702", "Eastern Himalayan Zone", "Red & Lateritic Soil"),
        ("Gangtok", "Sikkim", "SK", 27.3389, 88.6065, "710", "Eastern Himalayan Zone", "Red & Lateritic Soil"),
        ("Tawang", "Arunachal Pradesh", "AR", 27.5861, 91.8692, "721", "Eastern Himalayan Zone", "Red & Lateritic Soil"),
        ("Itanagar", "Arunachal Pradesh", "AR", 27.0844, 93.6053, "722", "Eastern Himalayan Zone", "Red & Lateritic Soil"),
        ("Pasighat", "Arunachal Pradesh", "AR", 28.0667, 95.3333, "723", "Eastern Himalayan Zone", "Red & Lateritic Soil"),
        
        # Zone 3: Lower Gangetic Plains Zone
        ("Kolkata", "West Bengal", "WB", 22.5726, 88.3639, "703", "Lower Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Howrah", "West Bengal", "WB", 22.5958, 88.2636, "704", "Lower Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Nadia", "West Bengal", "WB", 23.4729, 88.5011, "705", "Lower Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Murshidabad", "West Bengal", "WB", 24.1800, 88.2700, "706", "Lower Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Malda", "West Bengal", "WB", 25.1800, 88.1300, "707", "Lower Gangetic Plains Zone", "Gangetic Alluvial"),
        ("North 24 Parganas", "West Bengal", "WB", 22.7196, 88.6866, "708", "Lower Gangetic Plains Zone", "Gangetic Alluvial"),
        ("South 24 Parganas", "West Bengal", "WB", 22.1700, 88.5100, "709", "Lower Gangetic Plains Zone", "Gangetic Alluvial"),
        
        # Zone 4: Middle Gangetic Plains Zone
        ("Patna", "Bihar", "BR", 25.5941, 85.1376, "801", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Gaya", "Bihar", "BR", 24.7914, 84.9949, "802", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Muzaffarpur", "Bihar", "BR", 26.1209, 85.3647, "803", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Darbhanga", "Bihar", "BR", 26.1570, 85.8966, "804", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Bhagalpur", "Bihar", "BR", 25.2425, 86.9843, "805", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Purnia", "Bihar", "BR", 25.7781, 87.4761, "806", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Varanasi", "Uttar Pradesh", "UP", 25.3176, 82.9739, "221", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Allahabad", "Uttar Pradesh", "UP", 25.4358, 81.8463, "222", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Gorakhpur", "Uttar Pradesh", "UP", 26.7606, 83.3732, "223", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        ("Azamgarh", "Uttar Pradesh", "UP", 26.0700, 83.1900, "224", "Middle Gangetic Plains Zone", "Gangetic Alluvial"),
        
        # Zone 5: Upper Gangetic Plains Zone
        ("Delhi", "Delhi", "DL", 28.7041, 77.1025, "101", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Meerut", "Uttar Pradesh", "UP", 28.9845, 77.7064, "225", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Ghaziabad", "Uttar Pradesh", "UP", 28.6692, 77.4538, "226", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Moradabad", "Uttar Pradesh", "UP", 28.8386, 78.7733, "227", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Bareilly", "Uttar Pradesh", "UP", 28.3670, 79.4304, "228", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Saharanpur", "Uttar Pradesh", "UP", 29.9680, 77.5552, "229", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Aligarh", "Uttar Pradesh", "UP", 27.8974, 78.0880, "230", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Mathura", "Uttar Pradesh", "UP", 27.4924, 77.6737, "231", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Agra", "Uttar Pradesh", "UP", 27.1767, 78.0081, "232", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Kanpur", "Uttar Pradesh", "UP", 26.4499, 80.3319, "233", "Upper Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        
        # Zone 6: Trans-Gangetic Plains Zone
        ("Ludhiana", "Punjab", "PB", 30.9010, 75.8573, "301", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Amritsar", "Punjab", "PB", 31.6340, 74.8723, "302", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Jalandhar", "Punjab", "PB", 31.3260, 75.5762, "303", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Patiala", "Punjab", "PB", 30.3398, 76.3869, "304", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Bathinda", "Punjab", "PB", 30.2110, 74.9455, "305", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Gurdaspur", "Punjab", "PB", 32.0377, 75.4078, "306", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Hoshiarpur", "Punjab", "PB", 31.5325, 75.9113, "307", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Firozpur", "Punjab", "PB", 30.9258, 74.6123, "308", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Kapurthala", "Punjab", "PB", 31.3800, 75.3800, "309", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Chandigarh", "Chandigarh", "CH", 30.7333, 76.7794, "110", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Ambala", "Haryana", "HR", 30.3752, 76.7821, "401", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Karnal", "Haryana", "HR", 29.6857, 76.9905, "402", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Kurukshetra", "Haryana", "HR", 29.9695, 76.8783, "403", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Panipat", "Haryana", "HR", 29.3909, 76.9635, "404", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Sonipat", "Haryana", "HR", 28.9931, 77.0151, "405", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Rohtak", "Haryana", "HR", 28.8955, 76.6066, "406", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Hisar", "Haryana", "HR", 29.1492, 75.7217, "407", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        ("Sirsa", "Haryana", "HR", 29.5318, 75.0210, "408", "Trans-Gangetic Plains Zone", "Indo-Gangetic Alluvial"),
        
        # Zone 7: Eastern Plateau and Hills Zone
        ("Ranchi", "Jharkhand", "JH", 23.3441, 85.3096, "901", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Jamshedpur", "Jharkhand", "JH", 22.8046, 86.2029, "902", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Dhanbad", "Jharkhand", "JH", 23.7957, 86.4304, "903", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Bokaro", "Jharkhand", "JH", 23.6693, 86.1511, "904", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Hazaribagh", "Jharkhand", "JH", 23.9989, 85.3634, "905", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Bhubaneswar", "Odisha", "OD", 20.2961, 85.8245, "1001", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Cuttack", "Odisha", "OD", 20.4625, 85.8828, "1002", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Rourkela", "Odisha", "OD", 22.2604, 84.8536, "1003", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Sambalpur", "Odisha", "OD", 21.4669, 83.9812, "1004", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Balasore", "Odisha", "OD", 21.4918, 86.9323, "1005", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Koraput", "Odisha", "OD", 18.8167, 82.7167, "1006", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Mayurbhanj", "Odisha", "OD", 21.9400, 86.7200, "1007", "Eastern Plateau and Hills Zone", "Red & Lateritic Soil"),
        
        # Zone 8: Central Plateau and Hills Zone
        ("Bhopal", "Madhya Pradesh", "MP", 23.2599, 77.4126, "501", "Central Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Indore", "Madhya Pradesh", "MP", 22.7196, 75.8577, "502", "Central Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Jabalpur", "Madhya Pradesh", "MP", 23.1815, 79.9864, "503", "Central Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Gwalior", "Madhya Pradesh", "MP", 26.2183, 78.1828, "504", "Central Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Ujjain", "Madhya Pradesh", "MP", 23.1765, 75.7885, "505", "Central Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Sagar", "Madhya Pradesh", "MP", 23.8365, 78.7365, "506", "Central Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Raipur", "Chhattisgarh", "CG", 21.2514, 81.6296, "510", "Central Plateau and Hills Zone", "Red & Yellow Soil"),
        ("Bilaspur", "Chhattisgarh", "CG", 22.0797, 82.1409, "511", "Central Plateau and Hills Zone", "Red & Yellow Soil"),
        ("Durg", "Chhattisgarh", "CG", 21.1900, 81.2800, "512", "Central Plateau and Hills Zone", "Red & Yellow Soil"),
        ("Korba", "Chhattisgarh", "CG", 22.3595, 82.7501, "513", "Central Plateau and Hills Zone", "Red & Yellow Soil"),
        ("Rajnandgaon", "Chhattisgarh", "CG", 21.1000, 81.0300, "514", "Central Plateau and Hills Zone", "Red & Yellow Soil"),
        
        # Zone 9: Western Plateau and Hills Zone
        ("Mumbai", "Maharashtra", "MH", 19.0760, 72.8777, "401", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Pune", "Maharashtra", "MH", 18.5204, 73.8567, "402", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Nashik", "Maharashtra", "MH", 19.9975, 73.7898, "403", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Aurangabad", "Maharashtra", "MH", 19.8762, 75.3433, "404", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Nagpur", "Maharashtra", "MH", 21.1458, 79.0882, "405", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Solapur", "Maharashtra", "MH", 17.6599, 75.9064, "406", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Kolhapur", "Maharashtra", "MH", 16.7050, 74.2433, "407", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Sangli", "Maharashtra", "MH", 16.8524, 74.5815, "408", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Ahmednagar", "Maharashtra", "MH", 19.0948, 74.7480, "409", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Dhule", "Maharashtra", "MH", 20.9042, 74.7749, "410", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Jalgaon", "Maharashtra", "MH", 21.0077, 75.5626, "411", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Latur", "Maharashtra", "MH", 18.4088, 76.5604, "412", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Nanded", "Maharashtra", "MH", 19.1383, 77.3210, "413", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Parbhani", "Maharashtra", "MH", 19.2618, 76.7748, "414", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Beed", "Maharashtra", "MH", 18.9896, 75.7600, "415", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Osmanabad", "Maharashtra", "MH", 18.1820, 76.0385, "416", "Western Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        
        # Zone 10: Southern Plateau and Hills Zone
        ("Bengaluru Urban", "Karnataka", "KA", 12.9716, 77.5946, "562", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Bengaluru Rural", "Karnataka", "KA", 13.0900, 77.5600, "563", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Mysuru", "Karnataka", "KA", 12.2958, 76.6394, "564", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Mandya", "Karnataka", "KA", 12.5240, 76.8970, "565", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Hassan", "Karnataka", "KA", 13.0049, 76.1008, "566", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Chikkamagaluru", "Karnataka", "KA", 13.3161, 75.7720, "567", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Shivamogga", "Karnataka", "KA", 13.9299, 75.5681, "568", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Davanagere", "Karnataka", "KA", 14.4644, 75.9218, "569", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Ballari", "Karnataka", "KA", 15.1394, 76.9214, "570", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Kalaburagi", "Karnataka", "KA", 17.3297, 76.8343, "571", "Southern Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Belagavi", "Karnataka", "KA", 15.8497, 74.4977, "572", "Southern Plateau and Hills Zone", "Red & Lateritic Soil"),
        ("Vijayapura", "Karnataka", "KA", 16.8302, 75.7100, "573", "Southern Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Bagalkot", "Karnataka", "KA", 16.1850, 75.7000, "574", "Southern Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Raichur", "Karnataka", "KA", 16.2076, 77.3560, "575", "Southern Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Koppal", "Karnataka", "KA", 15.3500, 76.1500, "576", "Southern Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Gadag", "Karnataka", "KA", 15.4255, 75.6321, "577", "Southern Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Dharwad", "Karnataka", "KA", 15.4589, 75.0078, "578", "Southern Plateau and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Uttara Kannada", "Karnataka", "KA", 14.6880, 74.5760, "579", "Southern Plateau and Hills Zone", "Lateritic Soil"),
        ("Udupi", "Karnataka", "KA", 13.3409, 74.7421, "580", "Southern Plateau and Hills Zone", "Lateritic Soil"),
        ("Dakshina Kannada", "Karnataka", "KA", 12.8438, 74.8327, "581", "Southern Plateau and Hills Zone", "Lateritic Soil"),
        
        # Zone 11: East Coast Plains and Hills Zone
        ("Chennai", "Tamil Nadu", "TN", 13.0827, 80.2707, "600", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Kanchipuram", "Tamil Nadu", "TN", 12.8342, 79.7036, "601", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Tiruvallur", "Tamil Nadu", "TN", 13.1438, 79.9089, "602", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Vellore", "Tamil Nadu", "TN", 12.9165, 79.1325, "603", "East Coast Plains and Hills Zone", "Red Loam"),
        ("Tiruvannamalai", "Tamil Nadu", "TN", 12.2260, 79.0710, "604", "East Coast Plains and Hills Zone", "Red Loam"),
        ("Viluppuram", "Tamil Nadu", "TN", 11.9398, 79.4861, "605", "East Coast Plains and Hills Zone", "Red Loam"),
        ("Cuddalore", "Tamil Nadu", "TN", 11.7463, 79.7714, "606", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Nagapattinam", "Tamil Nadu", "TN", 10.7666, 79.8428, "607", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Thanjavur", "Tamil Nadu", "TN", 10.7870, 79.1378, "608", "East Coast Plains and Hills Zone", "Cauvery Delta Alluvial"),
        ("Tiruvarur", "Tamil Nadu", "TN", 10.7727, 79.6368, "609", "East Coast Plains and Hills Zone", "Cauvery Delta Alluvial"),
        ("Pudukkottai", "Tamil Nadu", "TN", 10.3813, 78.8204, "610", "East Coast Plains and Hills Zone", "Red Loam"),
        ("Ramanathapuram", "Tamil Nadu", "TN", 9.3687, 78.8343, "611", "East Coast Plains and Hills Zone", "Coastal Sandy"),
        ("Virudhunagar", "Tamil Nadu", "TN", 9.5852, 77.9580, "612", "East Coast Plains and Hills Zone", "Red Loam"),
        ("Tirunelveli", "Tamil Nadu", "TN", 8.7139, 77.7567, "613", "East Coast Plains and Hills Zone", "Red Loam"),
        ("Thoothukudi", "Tamil Nadu", "TN", 8.7642, 78.1348, "614", "East Coast Plains and Hills Zone", "Coastal Sandy"),
        ("Kanyakumari", "Tamil Nadu", "TN", 8.0883, 77.5385, "615", "East Coast Plains and Hills Zone", "Red Loam"),
        ("Visakhapatnam", "Andhra Pradesh", "AP", 17.6868, 83.2185, "620", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Vijayawada", "Andhra Pradesh", "AP", 16.5062, 80.6480, "621", "East Coast Plains and Hills Zone", "Krishna Delta Alluvial"),
        ("Guntur", "Andhra Pradesh", "AP", 16.3067, 80.4365, "622", "East Coast Plains and Hills Zone", "Krishna Delta Alluvial"),
        ("Nellore", "Andhra Pradesh", "AP", 14.4426, 79.9865, "623", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Kakinada", "Andhra Pradesh", "AP", 16.9891, 82.2475, "624", "East Coast Plains and Hills Zone", "Godavari Delta Alluvial"),
        ("Rajahmundry", "Andhra Pradesh", "AP", 17.0005, 81.7675, "625", "East Coast Plains and Hills Zone", "Godavari Delta Alluvial"),
        ("Eluru", "Andhra Pradesh", "AP", 16.7107, 81.1015, "626", "East Coast Plains and Hills Zone", "Godavari Delta Alluvial"),
        ("Srikakulam", "Andhra Pradesh", "AP", 18.2969, 83.8973, "627", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Vizianagaram", "Andhra Pradesh", "AP", 18.1148, 83.4153, "628", "East Coast Plains and Hills Zone", "Coastal Alluvial"),
        
        # Zone 12: West Coast Plains and Hills Zone
        ("Thiruvananthapuram", "Kerala", "KL", 8.5241, 76.9366, "651", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Kollam", "Kerala", "KL", 8.8932, 76.6141, "652", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Alappuzha", "Kerala", "KL", 9.4981, 76.3388, "653", "West Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Kottayam", "Kerala", "KL", 9.5916, 76.5222, "654", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Ernakulam", "Kerala", "KL", 9.9816, 76.2999, "655", "West Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Idukki", "Kerala", "KL", 9.8480, 76.9713, "656", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Thrissur", "Kerala", "KL", 10.5276, 76.2144, "657", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Palakkad", "Kerala", "KL", 10.7867, 76.6548, "658", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Malappuram", "Kerala", "KL", 11.0587, 76.0754, "659", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Kozhikode", "Kerala", "KL", 11.2588, 75.7804, "660", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Wayanad", "Kerala", "KL", 11.6854, 76.1320, "661", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Kannur", "Kerala", "KL", 11.8745, 75.3704, "662", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Kasaragod", "Kerala", "KL", 12.5065, 74.9821, "663", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Mangaluru", "Karnataka", "KA", 12.9141, 74.8560, "582", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Udupi", "Karnataka", "KA", 13.3409, 74.7421, "583", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("North Goa", "Goa", "GA", 15.4989, 73.8278, "671", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("South Goa", "Goa", "GA", 15.2993, 74.1240, "672", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Mumbai Suburban", "Maharashtra", "MH", 19.1197, 72.9056, "417", "West Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Thane", "Maharashtra", "MH", 19.2183, 72.9781, "418", "West Coast Plains and Hills Zone", "Coastal Alluvial"),
        ("Raigad", "Maharashtra", "MH", 18.5158, 73.1821, "419", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Ratnagiri", "Maharashtra", "MH", 16.9902, 73.3120, "420", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        ("Sindhudurg", "Maharashtra", "MH", 16.1736, 73.6358, "421", "West Coast Plains and Hills Zone", "Lateritic Soil"),
        
        # Zone 13: Gujarat Plains and Hills Zone
        ("Ahmedabad", "Gujarat", "GJ", 23.0225, 72.5714, "380", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Surat", "Gujarat", "GJ", 21.1702, 72.8311, "381", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Vadodara", "Gujarat", "GJ", 22.3072, 73.1812, "382", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Rajkot", "Gujarat", "GJ", 22.3039, 70.8022, "383", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Bhavnagar", "Gujarat", "GJ", 21.7645, 72.1519, "384", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Jamnagar", "Gujarat", "GJ", 22.4707, 70.0577, "385", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Junagadh", "Gujarat", "GJ", 21.5222, 70.4579, "386", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Gandhinagar", "Gujarat", "GJ", 23.2156, 72.6369, "387", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Anand", "Gujarat", "GJ", 22.5645, 72.9289, "388", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Kheda", "Gujarat", "GJ", 22.7556, 72.6853, "389", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Panchmahal", "Gujarat", "GJ", 22.3039, 73.6000, "390", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Dahod", "Gujarat", "GJ", 22.8333, 74.2500, "391", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Banaskantha", "Gujarat", "GJ", 24.1711, 72.4386, "392", "Gujarat Plains and Hills Zone", "Sandy Loam"),
        ("Patan", "Gujarat", "GJ", 23.8536, 72.1200, "393", "Gujarat Plains and Hills Zone", "Sandy Loam"),
        ("Mehsana", "Gujarat", "GJ", 23.5880, 72.3697, "394", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Sabarkantha", "Gujarat", "GJ", 23.0300, 73.0500, "395", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Kutch", "Gujarat", "GJ", 23.2410, 69.6669, "396", "Gujarat Plains and Hills Zone", "Rann / Saline Soil"),
        ("Surendranagar", "Gujarat", "GJ", 22.7211, 71.6486, "397", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Amreli", "Gujarat", "GJ", 21.6039, 71.2219, "398", "Gujarat Plains and Hills Zone", "Black Cotton / Medium Black Soil"),
        ("Bharuch", "Gujarat", "GJ", 21.7051, 72.9960, "399", "Gujarat Plains and Hills Zone", "Alluvial"),
        
        # Zone 14: Western Dry Zone
        ("Jaipur", "Rajasthan", "RJ", 26.9124, 75.7873, "302", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Jodhpur", "Rajasthan", "RJ", 26.2389, 73.0243, "303", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Bikaner", "Rajasthan", "RJ", 28.0229, 73.3119, "304", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Udaipur", "Rajasthan", "RJ", 24.5854, 73.7125, "305", "Western Dry Zone", "Red & Yellow Soil"),
        ("Kota", "Rajasthan", "RJ", 25.2138, 75.8648, "306", "Western Dry Zone", "Black Cotton / Medium Black Soil"),
        ("Ajmer", "Rajasthan", "RJ", 26.4499, 74.6399, "307", "Western Dry Zone", "Red & Yellow Soil"),
        ("Bhilwara", "Rajasthan", "RJ", 25.3470, 74.6328, "308", "Western Dry Zone", "Red & Yellow Soil"),
        ("Alwar", "Rajasthan", "RJ", 27.5530, 76.6346, "309", "Western Dry Zone", "Sandy Loam"),
        ("Bharatpur", "Rajasthan", "RJ", 27.2152, 77.4924, "310", "Western Dry Zone", "Alluvial"),
        ("Sikar", "Rajasthan", "RJ", 27.6094, 75.1399, "311", "Western Dry Zone", "Sandy Loam"),
        ("Nagaur", "Rajasthan", "RJ", 27.2038, 73.7365, "312", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Pali", "Rajasthan", "RJ", 25.7725, 73.3234, "313", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Jalore", "Rajasthan", "RJ", 25.3455, 72.6272, "314", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Barmer", "Rajasthan", "RJ", 25.7494, 71.4183, "315", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Jaisalmer", "Rajasthan", "RJ", 26.9157, 70.9160, "316", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Sri Ganganagar", "Rajasthan", "RJ", 29.9038, 73.8772, "317", "Western Dry Zone", "Alluvial"),
        ("Hanumangarh", "Rajasthan", "RJ", 29.5818, 74.3294, "318", "Western Dry Zone", "Alluvial"),
        ("Churu", "Rajasthan", "RJ", 28.3021, 74.9629, "319", "Western Dry Zone", "Desert / Sandy Soil"),
        ("Jhunjhunu", "Rajasthan", "RJ", 28.1257, 75.3981, "320", "Western Dry Zone", "Sandy Loam"),
        
        # Zone 15: Islands Zone
        ("Port Blair", "Andaman & Nicobar", "AN", 11.6667, 92.7500, "851", "Islands Zone", "Coastal Alluvial"),
        ("Kavaratti", "Lakshadweep", "LD", 10.5667, 72.6417, "861", "Islands Zone", "Coral Sand"),
    ]
    
    added = 0
    for data in districts_data:
        name, state, state_code, lat, lon, district_code, zone, soil_type = data
        
        # Check if already exists
        existing = session.execute(
            select(District).where(District.district_code == district_code)
        ).scalar_one_or_none()
        if existing:
            continue
        
        district = District(
            name=name,
            state=state,
            state_code=state_code,
            district_code=district_code,
            latitude=lat,
            longitude=lon,
            agro_climatic_zone=zone,
            soil_type=soil_type,
        )
        session.add(district)
        added += 1
    
    session.commit()
    print(f"  Added {added} districts (total: {existing_count + added})")
    return added


def seed_soil_mappings(session: Session):
    """Seed district_soil_types mappings for all districts."""
    print("Seeding district-soil mappings...")
    
    existing_count = session.execute(select(func.count(DistrictSoilType.id))).scalar()
    if existing_count > 20:
        print(f"  Already {existing_count} mappings, skipping")
        return existing_count
    
    # Clear existing if few
    if existing_count > 0:
        session.execute(text("TRUNCATE TABLE district_soil_types RESTART IDENTITY CASCADE"))
        session.commit()
    
    districts = session.execute(select(District.id, District.district_code, District.agro_climatic_zone, District.soil_type)).all()
    soil_types = session.execute(select(SoilType.id, SoilType.name)).all()
    soil_type_map = {name: id for id, name in soil_types}
    
    # Zone to soil type mapping for predominant soil
    zone_soil = {
        "Western Himalayan Temperate Zone": "Mountain Forest / Podzolic Loam",
        "Eastern Himalayan Zone": "Red & Lateritic Soil",
        "Lower Gangetic Plains Zone": "Gangetic Alluvial",
        "Middle Gangetic Plains Zone": "Gangetic Alluvial",
        "Upper Gangetic Plains Zone": "Indo-Gangetic Alluvial",
        "Trans-Gangetic Plains Zone": "Indo-Gangetic Alluvial",
        "Eastern Plateau and Hills Zone": "Red & Lateritic Soil",
        "Central Plateau and Hills Zone": "Black Cotton / Medium Black Soil",
        "Western Plateau and Hills Zone": "Black Cotton / Medium Black Soil",
        "Southern Plateau and Hills Zone": "Red & Lateritic Soil",
        "East Coast Plains and Hills Zone": "Coastal Alluvial",
        "West Coast Plains and Hills Zone": "Lateritic Soil",
        "Gujarat Plains and Hills Zone": "Black Cotton / Medium Black Soil",
        "Western Dry Zone": "Desert / Sandy Soil",
        "Islands Zone": "Coastal Alluvial",
    }
    
    added = 0
    for dist_id, dist_code, zone, pred_soil in districts:
        pred_soil_id = soil_type_map.get(pred_soil)
        if pred_soil_id:
            mapping = DistrictSoilType(
                district_id=dist_id,
                soil_type_id=pred_soil_id,
                percentage=80.0,
                is_predominant=True,
            )
            session.add(mapping)
            added += 1
        
        # Add secondary soil type based on zone
        secondary_soils = {
            "Western Himalayan Temperate Zone": "Red & Lateritic Soil",
            "Eastern Himalayan Zone": "Mountain Forest / Podzolic Loam",
            "Lower Gangetic Plains Zone": "Red & Lateritic Soil",
            "Middle Gangetic Plains Zone": "Sandy Loam",
            "Upper Gangetic Plains Zone": "Sandy Loam",
            "Trans-Gangetic Plains Zone": "Sandy Loam",
            "Eastern Plateau and Hills Zone": "Black Cotton / Medium Black Soil",
            "Central Plateau and Hills Zone": "Red & Yellow Soil",
            "Western Plateau and Hills Zone": "Red & Lateritic Soil",
            "Southern Plateau and Hills Zone": "Black Cotton / Medium Black Soil",
            "East Coast Plains and Hills Zone": "Red Loam",
            "West Coast Plains and Hills Zone": "Coastal Alluvial",
            "Gujarat Plains and Hills Zone": "Sandy Loam",
            "Western Dry Zone": "Red & Yellow Soil",
            "Islands Zone": "Coral Sand",
        }
        sec_soil = secondary_soils.get(zone)
        sec_soil_id = soil_type_map.get(sec_soil) if sec_soil else None
        if sec_soil_id:
            mapping = DistrictSoilType(
                district_id=dist_id,
                soil_type_id=sec_soil_id,
                percentage=20.0,
                is_predominant=False,
            )
            session.add(mapping)
            added += 1
    
    session.commit()
    print(f"  Added {added} district-soil mappings")
    return added


def seed_crop_profiles(session: Session, crops_data: dict):
    
    # Get existing crop names to avoid duplicates
    existing = set()
    existing_query = session.execute(select(CropProfile.name)).scalars().all()
    existing = set(existing_query)
    
    added = 0
    for crop_type in ["short_term", "long_term"]:
        category = "short_term" if crop_type == "short_term" else "long_term"
        for crop in crops_data[crop_type]:
            if crop["name"] in existing:
                continue
                
            profile = CropProfile(
                name=crop["name"],
                common_name=crop["name"],
                category=category,
                season=crop["season"],
                description=f"{crop['name']} - {crop['season']} crop, {crop['duration_days']} days duration",
                suitable_soil_types=crop.get("suitable_soils", []),
                ph_min=crop["soil_ph_range"][0] if crop.get("soil_ph_range") else 5.5,
                ph_max=crop["soil_ph_range"][1] if crop.get("soil_ph_range") else 8.0,
                rainfall_min_mm=crop["rainfall_range_mm"][0] if crop.get("rainfall_range_mm") else 300,
                rainfall_max_mm=crop["rainfall_range_mm"][1] if crop.get("rainfall_range_mm") else 2000,
                temp_min_c=crop["temp_range_c"][0] if crop.get("temp_range_c") else 10,
                temp_max_c=crop["temp_range_c"][1] if crop.get("temp_range_c") else 35,
                n_requirement=crop.get("opt_n", 100),
                p_requirement=crop.get("opt_p", 40),
                k_requirement=crop.get("opt_k", 40),
                spacing_cm=30.0,
                row_spacing_cm=60.0,
                duration_days=crop["duration_days"],
                expected_yield_tons_per_ha=crop["base_yield_t_ha"],
                water_requirement_mm=crop["water_mm"],
            )
            session.add(profile)
            added += 1
    
    session.commit()
    print(f"  Added {added} crop profiles")
    return added


def seed_crop_costs(session: Session):
    """Seed crop_costs table with realistic cost data for each crop."""
    print("Seeding crop_costs...")
    
    # Check existing
    existing_count = session.execute(select(func.count(CropCost.id))).scalar()
    if existing_count > 0:
        print(f"  Already {existing_count} cost records, skipping")
        return 0
    
    crops = session.execute(select(CropProfile.id, CropProfile.name)).all()
    districts = session.execute(select(District.id, District.name, District.state)).all()
    
    # Standard cost activities for crops
    cost_activities = [
        ("Land Preparation", "hectare", 3500, 1.0),
        ("Seeds/Planting Material", "hectare", 2500, 1.0),
        ("Fertilizers & Manures", "hectare", 4000, 1.0),
        ("Plant Protection", "hectare", 2000, 1.0),
        ("Irrigation", "hectare", 1500, 1.0),
        ("Labour - Sowing/Transplanting", "hectare", 3000, 1.0),
        ("Labour - Weeding", "hectare", 2500, 1.0),
        ("Labour - Harvesting", "hectare", 4000, 1.0),
        ("Post-Harvest Handling", "hectare", 1500, 1.0),
        ("Transportation", "hectare", 2000, 1.0),
        ("Miscellaneous", "hectare", 1000, 1.0),
    ]
    
    added = 0
    for crop_id, crop_name in crops:
        # National level costs (district_id = None)
        for activity, unit, base_cost, quantity in cost_activities:
            # Vary costs by crop type
            multiplier = 1.0
            if "Rice" in crop_name or "Wheat" in crop_name:
                multiplier = 1.2
            elif "Cotton" in crop_name or "Sugarcane" in crop_name:
                multiplier = 1.5
            elif "Coconut" in crop_name or "Mango" in crop_name:
                multiplier = 1.3
            elif "Banana" in crop_name:
                multiplier = 1.8
            
            cost = CropCost(
                crop_id=crop_id,
                district_id=None,  # National level
                activity=activity,
                unit=unit,
                unit_cost=round(base_cost * multiplier * random.uniform(0.9, 1.1)),
                quantity_per_ha=quantity,
                region="national",
                validity_start=date(2024, 1, 1),
                validity_end=date(2025, 12, 31),
                source="AgriBrain Cost Database 2024",
            )
            session.add(cost)
            added += 1
        
        # Add regional variations for 3 random districts
        for dist_id, dist_name, dist_state in random.sample(districts, min(3, len(districts))):
            for activity, unit, base_cost, quantity in cost_activities[:5]:  # Fewer regional entries
                cost = CropCost(
                    crop_id=crop_id,
                    district_id=dist_id,
                    activity=activity,
                    unit=unit,
                    unit_cost=round(base_cost * random.uniform(0.85, 1.15)),
                    quantity_per_ha=quantity,
                    region=dist_state,
                    validity_start=date(2024, 1, 1),
                    validity_end=date(2025, 12, 31),
                    source=f"Regional Cost Survey {dist_state} 2024",
                )
                session.add(cost)
                added += 1
    
    session.commit()
    print(f"  Added {added} crop cost records")
    return added


def seed_crop_prices(session: Session):
    """Seed crop_prices table with realistic market price data."""
    print("Seeding crop_prices...")
    
    existing_count = session.execute(select(func.count(CropPrice.id))).scalar()
    if existing_count > 50:
        print(f"  Already {existing_count} price records, skipping")
        return 0
    
    crops = session.execute(select(CropProfile.id, CropProfile.name, CropProfile.expected_yield_tons_per_ha)).all()
    
    markets = [
        "Bangalore APMC", "Delhi Azadpur", "Mumbai Vashi", "Hyderabad Bowenpally",
        "Chennai Koyambedu", "Kolkata Posta", "Pune Market Yard", "Ahmedabad APMC",
        "Lucknow Mandi", "Jaipur Muhana", "Coimbatore", "Nashik", "Indore",
        "Vijayawada", "Guntur", "Raichur", "Davangere", "Sangli"
    ]
    
    added = 0
    for crop_id, crop_name, yield_tons in crops:
        # Base price around realistic market rates per tonne
        # Use yield to estimate value category: high yield = lower price per tonne typically
        if yield_tons and yield_tons > 20:
            base_price = 12000  # High yield crops (vegetables, fruits)
        elif yield_tons and yield_tons > 5:
            base_price = 25000  # Medium yield crops
        else:
            base_price = 45000  # Low yield crops (pulses, oilseeds, spices)
        
        for market in random.sample(markets, min(8, len(markets))):
            # Generate prices for last 60 days
            for days_back in range(0, 60, 7):  # Weekly prices
                price_date = date.today() - timedelta(days=days_back)
                # Market price varies around MSP
                variation = random.uniform(0.85, 1.25)
                market_price = round(base_price * variation)
                
                price = CropPrice(
                    crop_id=crop_id,
                    market=market,
                    price_per_ton=market_price,
                    price_date=price_date,
                    source="AgriMarket Watch",
                )
                session.add(price)
                added += 1
    
    session.commit()
    print(f"  Added {added} crop price records")
    return added


def seed_rainfall_monthly(session: Session):
    """Seed rainfall_monthly with historical data for each district."""
    print("Seeding rainfall_monthly...")
    
    existing_count = session.execute(select(func.count(RainfallMonthly.id))).scalar()
    if existing_count > 0:
        print(f"  Already {existing_count} rainfall records, skipping")
        return 0
    
    districts = session.execute(select(District.id, District.name, District.agro_climatic_zone)).all()
    
    # Zone-based average monthly rainfall (mm) - 15 ICAR Agro-Climatic Zones
    zone_rainfall = {
        "Western Himalayan Temperate Zone": [80, 70, 60, 40, 30, 40, 120, 130, 100, 50, 30, 50],
        "Eastern Himalayan Zone": [20, 15, 30, 80, 200, 400, 500, 450, 300, 150, 40, 20],
        "Lower Gangetic Plains Zone": [15, 10, 20, 40, 100, 250, 350, 300, 250, 100, 20, 10],
        "Middle Gangetic Plains Zone": [15, 10, 10, 15, 30, 100, 300, 280, 200, 60, 10, 5],
        "Upper Gangetic Plains Zone": [20, 15, 15, 10, 20, 80, 250, 220, 150, 40, 10, 10],
        "Trans-Gangetic Plains Zone": [20, 15, 15, 10, 20, 80, 250, 220, 150, 40, 10, 10],
        "Eastern Plateau and Hills Zone": [15, 15, 20, 30, 60, 180, 300, 280, 200, 80, 20, 10],
        "Central Plateau and Hills Zone": [10, 10, 10, 10, 20, 120, 280, 260, 180, 60, 15, 10],
        "Western Plateau and Hills Zone": [5, 5, 10, 20, 50, 120, 180, 160, 140, 120, 40, 10],
        "Southern Plateau and Hills Zone": [5, 5, 10, 30, 80, 150, 200, 180, 150, 150, 60, 20],
        "East Coast Plains and Hills Zone": [20, 10, 10, 20, 60, 100, 120, 140, 150, 250, 300, 100],
        "West Coast Plains and Hills Zone": [5, 5, 5, 30, 150, 600, 800, 600, 400, 250, 100, 20],
        "Gujarat Plains and Hills Zone": [5, 5, 5, 5, 10, 80, 250, 200, 150, 40, 10, 5],
        "Western Dry Zone": [5, 5, 5, 5, 10, 40, 120, 100, 60, 15, 5, 5],
        "Islands Zone": [50, 30, 20, 50, 150, 300, 350, 300, 250, 200, 150, 80],
    }
    
    added = 0
    for dist_id, dist_name, zone in districts:
        monthly_avg = zone_rainfall.get(zone, [50]*12)
        
        for year in [2022, 2023, 2024]:
            for month in range(1, 13):
                # Add some random variation
                base_rain = monthly_avg[month - 1]
                rainfall = round(base_rain * random.uniform(0.7, 1.3), 1)
                
                record = RainfallMonthly(
                    district_id=dist_id,
                    year=year,
                    month=month,
                    rainfall_mm=rainfall,
                    source="IMD Historical" if year < 2024 else "IMD Live",
                )
                session.add(record)
                added += 1
    
    session.commit()
    print(f"  Added {added} monthly rainfall records")
    return added


def seed_rainfall_forecasts(session: Session):
    """Seed rainfall_forecasts with 14-day forecasts for each district."""
    print("Seeding rainfall_forecasts...")
    
    existing_count = session.execute(select(func.count(RainfallForecast.id))).scalar()
    if existing_count > 0:
        print(f"  Already {existing_count} forecast records, skipping")
        return 0
    
    districts = session.execute(select(District.id)).scalars().all()
    
    added = 0
    for dist_id in districts:
        # Generate 14-day forecast starting tomorrow
        for day_offset in range(1, 15):
            forecast_date = date.today() + timedelta(days=day_offset)
            # Random forecast with seasonal bias
            base = random.uniform(0, 25)
            predicted = round(base, 1)
            lower = round(max(0, predicted - random.uniform(0, 10)), 1)
            upper = round(predicted + random.uniform(0, 15), 1)
            
            forecast = RainfallForecast(
                district_id=dist_id,
                forecast_date=forecast_date,
                predicted_mm=predicted,
                lower_bound_mm=lower,
                upper_bound_mm=upper,
                model_version="Open-Meteo Ensemble v1.0",
            )
            session.add(forecast)
            added += 1
    
    session.commit()
    print(f"  Added {added} rainfall forecast records")
    return added


def main():
    print("=" * 60)
    print("COMPREHENSIVE DATABASE SEEDING - PHASE 4")
    print("=" * 60)
    
    settings = get_settings()
    is_sqlite = settings.DATABASE_URL.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine_local = engine
    
    with Session(engine_local) as session:
        # 1. Seed districts (150+ pan-India)
        seed_districts(session)
        
        # 2. Seed soil mappings
        seed_soil_mappings(session)
        
        # 3. Load crops data
        crops_data = load_crops_master()
        total_crops = len(crops_data["short_term"]) + len(crops_data["long_term"])
        print(f"Loaded {total_crops} crops from crops_master.yaml")
        
        # 4. Seed crop_profiles
        seed_crop_profiles(session, crops_data)
        
        # 5. Seed crop_costs
        seed_crop_costs(session)
        
        # 6. Seed crop_prices
        seed_crop_prices(session)
        
        # 7. Seed rainfall_monthly
        seed_rainfall_monthly(session)
        
        # 8. Seed rainfall_forecasts
        seed_rainfall_forecasts(session)
    
    # Verification
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    with Session(engine_local) as session:
        from sqlalchemy import text
        tables = [
            "districts", "soil_types", "district_soil_types",
            "crop_profiles", "crop_costs", "crop_prices",
            "rainfall_monthly", "rainfall_forecasts"
        ]
        for table in tables:
            count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"  {table}: {count} rows")
    
    print("\n✅ Database seeding completed successfully!")


if __name__ == "__main__":
    main()