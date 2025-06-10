#!/usr/bin/env python3
"""
Extract producer ID to name mappings from load-summary data
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

def extract_producer_mappings():
    """Extract producer ID to name mappings from load-summary data"""
    
    print("🔍 Extracting producer mappings from load-summary data...")
    
    # Get data from the last few days to build a comprehensive mapping
    date_ranges = []
    for i in range(7):  # Last 7 days
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        date_ranges.append(date)
    
    producer_mapping = {}
    
    for date_str in date_ranges:
        print(f"\n📅 Fetching data for {date_str}...")
        
        url = f"{API_BASE_URL}/pickups/load-summary"
        params = {"start_date": date_str, "end_date": date_str}
        
        try:
            response = requests.get(url, headers=get_auth_headers(), params=params)
            response.raise_for_status()
            
            summaries = response.json()
            hauler_77_data = [s for s in summaries if s.get('hauler_number') == HAULER_NUMBER]
            
            print(f"  Found {len(hauler_77_data)} hauler 77 records")
            
            # Extract producer mappings
            for record in hauler_77_data:
                producer_id = record.get('producer_id')
                producer_name = record.get('producer_name')
                producer_tank = record.get('producer_tank', '1')
                
                if producer_id and producer_name:
                    if producer_id not in producer_mapping:
                        producer_mapping[producer_id] = {
                            'name': producer_name,
                            'tank': producer_tank,
                            'count': 0
                        }
                    producer_mapping[producer_id]['count'] += 1
                    
        except Exception as e:
            print(f"  ❌ Error for {date_str}: {e}")
    
    # Display the mapping
    print(f"\n" + "="*80)
    print(f"🎯 EXTRACTED PRODUCER ID MAPPINGS ({len(producer_mapping)} unique producers)")
    print("="*80)
    
    # Sort by count (most frequent first)
    sorted_producers = sorted(producer_mapping.items(), key=lambda x: x[1]['count'], reverse=True)
    
    print("\nPython dictionary format:")
    print("PRODUCER_ID_MAPPING = {")
    
    for producer_id, info in sorted_producers:
        name = info['name']
        count = info['count']
        print(f'    "{producer_id}": "{name}",  # {count} records')
    
    print("}")
    
    # Also show the IDs from our schedule sample for reference
    test_ids = ["60cce07b8ada14e90f0783d6", "60cce07b8ada14e90f0783bd", "60cce07b8ada14e90f0783bf"]
    print(f"\n🔍 Schedule sample IDs:")
    for test_id in test_ids:
        if test_id in producer_mapping:
            info = producer_mapping[test_id]
            print(f"  ✅ {test_id} -> {info['name']} (found {info['count']} times)")
        else:
            print(f"  ❌ {test_id} -> NOT FOUND in load-summary data")

if __name__ == "__main__":
    extract_producer_mappings() 