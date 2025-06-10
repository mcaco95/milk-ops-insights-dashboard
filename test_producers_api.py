#!/usr/bin/env python3
"""
Test the producers API to see the structure
"""

import requests
import json

# Configuration
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"

def get_auth_headers():
    return {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}

def test_producers_api():
    """Test the producers API"""
    
    url = f"{API_BASE_URL}/producers"
    
    print(f"🔍 Testing producers API: {url}")
    
    try:
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        
        producers = response.json()
        print(f"📊 Found {len(producers)} total producers")
        
        # Show a few samples
        if producers:
            print("\n📋 Sample producer records:")
            for i, producer in enumerate(producers[:5]):
                print(f"\n  {i+1}. ID: {producer.get('_id')}")
                print(f"     Name: {producer.get('name')}")
                print(f"     Keys: {list(producer.keys())}")
        
        # Look for specific IDs from our schedule sample
        test_ids = ["60cce07b8ada14e90f0783d6", "60cce07b8ada14e90f0783bd", "60cce07b8ada14e90f0783bf"]
        print(f"\n🎯 Looking for specific IDs from schedule: {test_ids}")
        
        found_ids = {}
        for producer in producers:
            producer_id = producer.get('_id')
            if producer_id in test_ids:
                found_ids[producer_id] = producer.get('name', 'Unknown')
        
        print(f"✅ Found matches: {found_ids}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_producers_api() 