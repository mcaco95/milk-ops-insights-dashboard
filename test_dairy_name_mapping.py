#!/usr/bin/env python3
"""
Simple API test for dairy name mapping functionality.
Tests the running Docker APIs directly.
"""

import requests
import json

def test_api_endpoints():
    """Test the main API endpoints"""
    
    base_url = "http://localhost:5000"
    
    print("=== Testing API Endpoints ===\n")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"  Response: {response.json()}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Health check failed: {e}")
    
    print()
    
    # Test tank data endpoint
    try:
        response = requests.get(f"{base_url}/api/tank-data", timeout=10)
        print(f"Tank data: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  Found {len(data)} barns")
            
            # Look specifically for T&K Barn 2 to test our fix
            for barn_name, tanks in data.items():
                print(f"  {barn_name}: {len(tanks)} tanks")
                
                # Show milking status for each tank
                milking_tanks = []
                for tank_name, tank_info in tanks.items():
                    if tank_info.get('milking_into') not in ['None', None, '']:
                        milking_tanks.append(f"{tank_name} ({tank_info['milking_into']})")
                
                if milking_tanks:
                    print(f"    Milking: {', '.join(milking_tanks)}")
                else:
                    print(f"    No active milking")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Tank data failed: {e}")
    
    print()
    
    # Test barns endpoint
    try:
        response = requests.get(f"{base_url}/api/barns", timeout=5)
        print(f"Barns list: {response.status_code}")
        if response.status_code == 200:
            barns = response.json()
            print(f"  Available barns: {barns}")
        else:
            print(f"  Error: {response.text}")
    except Exception as e:
        print(f"Barns list failed: {e}")

def test_specific_barn(barn_name="T&K Barn 2"):
    """Test a specific barn's data"""
    
    print(f"\n=== Testing {barn_name} Specifically ===\n")
    
    base_url = "http://localhost:5000"
    
    try:
        response = requests.get(f"{base_url}/api/tank-data", timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            if barn_name in data:
                barn_data = data[barn_name]
                print(f"✓ Found {barn_name} with {len(barn_data)} tanks")
                
                for tank_name, tank_info in barn_data.items():
                    volume = tank_info.get('current_volume', 0)
                    milking = tank_info.get('milking_into', 'None')
                    time_to_full = tank_info.get('time_to_full_hours', 0)
                    
                    print(f"  {tank_name}:")
                    print(f"    Volume: {volume:,.0f} lbs")
                    print(f"    Milking: {milking}")
                    print(f"    Time to full: {time_to_full:.1f} hours")
                
                # Check if any tanks are milking (our main fix)
                milking_tanks = [name for name, info in barn_data.items() 
                               if info.get('milking_into') not in ['None', None, '']]
                
                if milking_tanks:
                    print(f"\n✓ SUCCESS: {barn_name} shows {len(milking_tanks)} tanks milking!")
                else:
                    print(f"\n⚠ WARNING: {barn_name} shows no tanks milking")
            else:
                print(f"✗ {barn_name} not found in response")
                print(f"Available barns: {list(data.keys())}")
        else:
            print(f"API call failed: {response.status_code}")
    except Exception as e:
        print(f"Error testing {barn_name}: {e}")

if __name__ == "__main__":
    print("DairyMen - Simple API Test")
    print("=" * 40)
    print("Make sure Docker containers are running!")
    print()
    
    test_api_endpoints()
    test_specific_barn("T&K Barn 2")
    test_specific_barn("T&K Barn 3")
    
    print("\n" + "=" * 40)
    print("Test completed!") 