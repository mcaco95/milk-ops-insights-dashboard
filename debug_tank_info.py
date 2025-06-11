#!/usr/bin/env python3

import requests
import re
from datetime import datetime

# API credentials
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

def check_mm_tank_info():
    """Check tank information from Milk Movement API"""
    print("=== MILK MOVEMENT TANK INFO ===")
    
    headers = {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Check schedules for tank info
    schedule_url = "https://api.prod.milkmoovement.io/v1/schedules"
    schedule_params = {"start_date": today, "end_date": today}
    
    try:
        response = requests.get(schedule_url, headers=headers, params=schedule_params)
        response.raise_for_status()
        schedules = response.json()
        
        # Filter hauler 77 and look at tank info
        hauler_77_schedules = [s for s in schedules if s.get('hauler', {}).get('hauler_number') == '77']
        
        print(f"Found {len(hauler_77_schedules)} hauler 77 schedules")
        
        if hauler_77_schedules:
            sample = hauler_77_schedules[0]
            print(f"\nSample schedule fields:")
            for key, value in sample.items():
                if 'tank' in key.lower() or key in ['route_name', 'lt_number']:
                    print(f"  {key}: {value}")
                    
        return hauler_77_schedules
        
    except Exception as e:
        print(f"Error: {e}")
        return []

def check_samsara_tank_info():
    """Check tank information from Samsara route names"""
    print("\n=== SAMSARA TANK INFO ===")
    
    url = "https://api.samsara.com/fleet/routes"
    headers = {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}
    
    today = datetime.now()
    params = {
        "startTime": today.replace(hour=0, minute=0, second=0).isoformat() + "Z",
        "endTime": today.replace(hour=23, minute=59, second=59).isoformat() + "Z",
        "limit": 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        routes = data.get('data', [])
        print(f"Found {len(routes)} Samsara routes")
        
        tank_patterns = []
        
        for route in routes[:10]:  # Check first 10 routes
            route_name = route.get('name', '')
            print(f"\nRoute: {route_name}")
            
            # Look for tank patterns
            tank_matches = re.findall(r'[Tt]ank\s*(\d+)', route_name)
            if tank_matches:
                print(f"  Tank numbers found: {tank_matches}")
                tank_patterns.extend(tank_matches)
            
            # Look for LT number
            lt_match = re.search(r'([A-Z]{3}\d{5})', route_name)
            if lt_match:
                print(f"  LT Number: {lt_match.group(1)}")
        
        print(f"\nUnique tank numbers found: {set(tank_patterns)}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    mm_data = check_mm_tank_info()
    check_samsara_tank_info() 