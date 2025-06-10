#!/usr/bin/env python3
"""
Debug script to see the actual structure of schedule API responses
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"
HAULER_NUMBER = "77"

def get_auth_headers():
    return {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}

def debug_schedule_structure():
    """Debug the actual structure of schedule records"""
    
    # Get today + tomorrow
    today = datetime.now().strftime("%Y-%m-%d")
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}/schedules"
    params = {"start_date": today, "end_date": tomorrow}
    
    print(f"🔍 Fetching schedules from {today} to {tomorrow}...")
    
    try:
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        
        schedules = response.json()
        print(f"📊 Found {len(schedules)} total schedules")
        
        # Filter to hauler 77
        hauler_77_schedules = []
        for schedule in schedules:
            hauler_info = schedule.get('hauler', {})
            if str(hauler_info.get('hauler_number', '')) == HAULER_NUMBER:
                hauler_77_schedules.append(schedule)
        
        print(f"🚛 Found {len(hauler_77_schedules)} schedules for hauler {HAULER_NUMBER}")
        
        if hauler_77_schedules:
            print("\n" + "="*80)
            print("📋 SAMPLE SCHEDULE RECORD STRUCTURE:")
            print("="*80)
            
            # Show the first schedule record structure
            sample = hauler_77_schedules[0]
            print(json.dumps(sample, indent=2))
            
            print("\n" + "="*80)
            print("🔑 KEY FIELDS IN ALL RECORDS:")
            print("="*80)
            
            # Analyze all records to see what fields exist
            all_keys = set()
            producer_fields = set()
            dairy_names = set()
            
            for schedule in hauler_77_schedules[:10]:  # Check first 10
                all_keys.update(schedule.keys())
                
                # Look for producer-related fields
                for key, value in schedule.items():
                    if 'producer' in key.lower() or 'dairy' in key.lower():
                        producer_fields.add(f"{key}: {type(value)}")
                        if isinstance(value, dict):
                            producer_fields.add(f"  {key} keys: {list(value.keys())}")
                        elif isinstance(value, str):
                            dairy_names.add(value)
            
            print("All top-level keys:")
            for key in sorted(all_keys):
                print(f"  - {key}")
            
            print("\nProducer/Dairy related fields:")
            for field in sorted(producer_fields):
                print(f"  - {field}")
            
            print("\nUnique dairy names found:")
            for name in sorted(dairy_names):
                print(f"  - '{name}'")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    debug_schedule_structure() 