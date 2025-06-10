#!/usr/bin/env python3
"""
Test the Milk Movement /schedules endpoint to find future routes
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"

def get_auth_headers():
    """Returns the authorization headers for Milk Movement API."""
    return {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}

def test_schedules_endpoint():
    """Test the /schedules endpoint to find future routes."""
    
    print("🗓️ TESTING MILK MOVEMENT SCHEDULES ENDPOINT")
    print("=" * 60)
    
    # Calculate date range
    now = datetime.now()
    start_date = (now - timedelta(hours=24)).strftime("%Y-%m-%d")
    end_date = (now + timedelta(hours=48)).strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}/schedules"
    
    # Try different parameter combinations
    test_params = [
        {"start_date": start_date, "end_date": end_date},
        {"date": end_date},  # Tomorrow only
        {"startDate": start_date, "endDate": end_date},  # Different naming
        {},  # No params
    ]
    
    for i, params in enumerate(test_params, 1):
        print(f"\n🧪 TEST {i}: {url}")
        print(f"📋 Parameters: {params}")
        print("-" * 40)
        
        try:
            response = requests.get(url, headers=get_auth_headers(), params=params)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ SUCCESS!")
                
                if isinstance(data, list):
                    print(f"📊 Found {len(data)} schedule records")
                    
                    if data:
                        # Show first record structure
                        print(f"\n🔍 First record sample:")
                        first_record = data[0]
                        for key, value in list(first_record.items())[:10]:  # First 10 fields
                            print(f"  {key}: {value}")
                        
                        if len(first_record) > 10:
                            print(f"  ... and {len(first_record) - 10} more fields")
                        
                        # Filter by hauler 77
                        hauler_77_schedules = []
                        for record in data:
                            hauler_num = str(record.get('hauler_number', record.get('hauler_id', '')))
                            if hauler_num == '77':
                                hauler_77_schedules.append(record)
                        
                        print(f"\n📦 Hauler 77 schedules: {len(hauler_77_schedules)}")
                        
                        if hauler_77_schedules:
                            # Group by date
                            from collections import defaultdict
                            by_date = defaultdict(int)
                            
                            for schedule in hauler_77_schedules:
                                # Look for date fields
                                date_fields = ['scheduled_date', 'pickup_date', 'date', 'start_date']
                                for field in date_fields:
                                    if field in schedule and schedule[field]:
                                        try:
                                            date_str = str(schedule[field])
                                            date_only = date_str.split('T')[0]
                                            by_date[date_only] += 1
                                            break
                                        except:
                                            continue
                            
                            if by_date:
                                print(f"📅 Hauler 77 schedules by date:")
                                for date, count in sorted(by_date.items()):
                                    marker = " ← TOMORROW!" if date == (now + timedelta(days=1)).strftime("%Y-%m-%d") else ""
                                    print(f"  {date}: {count} schedules{marker}")
                            
                            print(f"\n🎯 FOUND THE FUTURE ROUTES!")
                            print(f"   This is likely where your 46 tomorrow routes are!")
                            break
                        else:
                            print(f"❌ No hauler 77 schedules found")
                
                elif isinstance(data, dict):
                    print(f"📋 Response structure: {list(data.keys())}")
                    if 'data' in data:
                        schedules = data['data']
                        print(f"📊 Found {len(schedules)} schedule records in data field")
                else:
                    print(f"📋 Unexpected response type: {type(data)}")
                    
            elif response.status_code == 404:
                print(f"❌ Endpoint not found")
            elif response.status_code == 401:
                print(f"❌ Authentication failed")
            elif response.status_code == 400:
                print(f"❌ Bad request")
                print(f"Response: {response.text}")
            else:
                print(f"❌ Error {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
    
    print(f"\n💡 CONCLUSION:")
    print(f"If we found hauler 77 schedules above, that's where your")
    print(f"46 future routes are located - in /schedules, not /pickups!")

if __name__ == "__main__":
    test_schedules_endpoint() 