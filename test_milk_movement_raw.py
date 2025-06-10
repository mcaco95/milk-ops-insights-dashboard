#!/usr/bin/env python3
"""
Simple script to get the full raw payload from Milk Movement API
for the last 48 hours and next 24 hours
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

def get_milk_movement_data(start_date, end_date):
    """Get raw load summary data from Milk Movement API."""
    url = f"{API_BASE_URL}/pickups/load-summary"
    params = {
        "start_date": start_date,
        "end_date": end_date
    }
    
    print(f"🔍 Requesting data from: {start_date} to {end_date}")
    print(f"📡 API URL: {url}")
    print(f"📋 Parameters: {params}")
    print("-" * 50)
    
    try:
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ SUCCESS: Got {len(data) if isinstance(data, list) else 'unknown'} records")
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to fetch data: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Status Code: {e.response.status_code}")
            print(f"Response: {e.response.text}")
        return None

def main():
    """Main function to fetch and display raw Milk Movement data."""
    print("🥛 MILK MOVEMENT RAW DATA FETCHER")
    print("=" * 50)
    
    # Calculate date range: last 48 hours to next 24 hours
    now = datetime.now()
    start_date = (now - timedelta(hours=48)).strftime("%Y-%m-%d")
    end_date = (now + timedelta(hours=24)).strftime("%Y-%m-%d")
    
    print(f"📅 Date range: {start_date} to {end_date}")
    print(f"🕐 Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Fetch the raw data
    raw_data = get_milk_movement_data(start_date, end_date)
    
    if raw_data is None:
        print("❌ Failed to get data. Exiting.")
        return
    
    # Save to file
    output_file = f"milk_movement_raw_{start_date}_to_{end_date}.json"
    
    try:
        with open(output_file, 'w') as f:
            json.dump(raw_data, f, indent=2, default=str)
        print(f"💾 Raw data saved to: {output_file}")
    except Exception as e:
        print(f"❌ Failed to save file: {e}")
    
    # Display summary
    print("\n" + "=" * 50)
    print("📊 DATA SUMMARY")
    print("=" * 50)
    
    if isinstance(raw_data, list):
        print(f"Total records: {len(raw_data)}")
        
        if raw_data:
            # Show first record structure
            print("\n🔍 First record structure:")
            first_record = raw_data[0]
            for key, value in first_record.items():
                print(f"  {key}: {value}")
            
            # Group by date
            from collections import defaultdict
            dates = defaultdict(int)
            
            for record in raw_data:
                pickup_date = record.get('pickup_date', 'Unknown')
                if pickup_date and pickup_date != 'Unknown':
                    try:
                        date_only = pickup_date.split('T')[0]  # Get just the date part
                        dates[date_only] += 1
                    except:
                        dates[pickup_date] += 1
            
            print(f"\n📅 Records by date:")
            for date, count in sorted(dates.items()):
                print(f"  {date}: {count} records")
                
            # Show unique statuses if available
            statuses = set()
            dairy_names = set()
            
            for record in raw_data:
                if 'producer_name' in record:
                    dairy_names.add(record['producer_name'])
                    
                # Check for status-related fields
                for field in ['status', 'dropoff_date', 'geofence_enter_time']:
                    if field in record and record[field]:
                        statuses.add(f"{field}: has_data")
                    elif field in record:
                        statuses.add(f"{field}: empty")
            
            if dairy_names:
                print(f"\n🏭 Unique dairies ({len(dairy_names)}):")
                for dairy in sorted(dairy_names):
                    print(f"  - {dairy}")
            
            if statuses:
                print(f"\n📋 Status indicators:")
                for status in sorted(statuses):
                    print(f"  - {status}")
                    
    else:
        print(f"Data type: {type(raw_data)}")
        print(f"Data: {raw_data}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    main() 