#!/usr/bin/env python3
"""
Debug script to test combined route data and see what's in pickup_date fields
"""
import sys
import os
from datetime import datetime, date

# Add parent directory to import our routes script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from scripts.get_daily_routes import get_combined_routes_data, get_load_summaries, get_schedules_data

def debug_combined_data():
    """Debug the combined route data to see what's in pickup_date fields"""
    today = date.today().strftime("%Y-%m-%d")
    
    print("=== DEBUGGING COMBINED ROUTE DATA ===")
    print(f"Target date: {today}")
    
    # Test individual APIs first
    print("\n1. Testing Pickups API:")
    pickups = get_load_summaries(today)
    if pickups:
        print(f"Found {len(pickups)} pickup records")
        for i, pickup in enumerate(pickups[:3]):  # Show first 3
            print(f"Pickup {i+1}: pickup_date='{pickup.get('pickup_date')}', producer='{pickup.get('producer_name')}'")
    else:
        print("No pickup data found")
    
    print("\n2. Testing Schedules API:")
    schedules = get_schedules_data(today, today)
    if schedules:
        print(f"Found {len(schedules)} schedule records")
        for i, schedule in enumerate(schedules[:3]):  # Show first 3
            print(f"Schedule {i+1}: start_date='{schedule.get('start_date')}', route_name='{schedule.get('route_name')}'")
    else:
        print("No schedule data found")
    
    print("\n3. Testing Combined Data:")
    combined_data = get_combined_routes_data(today)
    
    if combined_data:
        print(f"Found {len(combined_data)} combined records")
        
        # Check both pickup and schedule records
        pickup_records = [r for r in combined_data if r.get('schedule_status') != 'scheduled']
        schedule_records = [r for r in combined_data if r.get('schedule_status') == 'scheduled']
        
        print(f"  - {len(pickup_records)} pickup records")
        print(f"  - {len(schedule_records)} schedule records")
        
        print("\nSample pickup records:")
        for i, record in enumerate(pickup_records[:3]):
            print(f"  Pickup {i+1}: pickup_date='{record.get('pickup_date')}', producer='{record.get('producer_name')}', truck='{record.get('truck_number')}'")
        
        print("\nSample schedule records:")
        for i, record in enumerate(schedule_records[:3]):
            print(f"  Schedule {i+1}: pickup_date='{record.get('pickup_date')}', producer='{record.get('producer_name')}', truck='{record.get('truck_number')}'")
        
        # Look for missing or malformed pickup_date
        missing_dates = [r for r in combined_data if not r.get('pickup_date')]
        invalid_dates = []
        
        for record in combined_data:
            pickup_date = record.get('pickup_date')
            if pickup_date:
                try:
                    # Try to parse the date
                    if isinstance(pickup_date, str) and 'T' in pickup_date:
                        # ISO format - should work
                        continue
                    else:
                        # Other format - might be problematic
                        datetime.strptime(str(pickup_date)[:10], "%Y-%m-%d")
                except:
                    invalid_dates.append(record)
        
        print(f"\nData quality check:")
        print(f"  - Records with missing pickup_date: {len(missing_dates)}")
        print(f"  - Records with invalid pickup_date format: {len(invalid_dates)}")
        
        if missing_dates:
            print("  Missing date examples:")
            for record in missing_dates[:2]:
                print(f"    - {record.get('producer_name')} / {record.get('route_number')}")
        
        if invalid_dates:
            print("  Invalid date examples:")
            for record in invalid_dates[:2]:
                print(f"    - {record.get('producer_name')}: '{record.get('pickup_date')}'")
    
    else:
        print("No combined data found")

if __name__ == "__main__":
    debug_combined_data() 