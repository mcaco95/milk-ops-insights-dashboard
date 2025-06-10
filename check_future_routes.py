#!/usr/bin/env python3
"""
Check future/scheduled routes for hauler 77
"""

import json
from collections import defaultdict, Counter
from datetime import datetime

def check_future_routes():
    """Check what future routes exist for hauler 77."""
    
    # Load the raw data file
    try:
        with open('milk_movement_raw_2025-06-07_to_2025-06-10.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Raw data file not found. Run test_milk_movement_raw.py first.")
        return
    
    print("🔮 FUTURE ROUTES ANALYSIS - HAULER 77")
    print("=" * 50)
    
    # Filter by hauler 77 only
    hauler_77_data = []
    for record in data:
        hauler_number = str(record.get('hauler_number', ''))
        if hauler_number == '77':
            hauler_77_data.append(record)
    
    print(f"📊 TOTAL HAULER 77 RECORDS: {len(hauler_77_data)}")
    
    # Group by date
    by_date = defaultdict(list)
    for record in hauler_77_data:
        pickup_date = record.get('pickup_date', '')
        if pickup_date:
            date_only = pickup_date.split('T')[0]
            by_date[date_only].append(record)
    
    print("\n📅 HAULER 77 RECORDS BY DATE:")
    print("-" * 30)
    for date in sorted(by_date.keys()):
        count = len(by_date[date])
        
        # Count unique routes for this date
        routes = set()
        for record in by_date[date]:
            truck_num = record.get('truck_number', 'Unknown')
            route_num = record.get('route_number', 'Unknown')
            routes.add(f"{route_num}-{truck_num}")
        
        status_marker = ""
        if date == "2025-06-09":
            status_marker = " ← TODAY"
        elif date == "2025-06-10":
            status_marker = " ← TOMORROW (FUTURE!)"
        elif date > "2025-06-09":
            status_marker = " ← FUTURE"
        
        print(f"{date}: {count} pickups, {len(routes)} routes{status_marker}")
    
    # Focus on future routes (2025-06-10 and beyond)
    future_dates = [date for date in by_date.keys() if date >= "2025-06-10"]
    
    if not future_dates:
        print("\n❌ NO FUTURE ROUTES FOUND FOR HAULER 77!")
        print("   This explains why you're not seeing scheduled routes.")
        return
    
    print(f"\n🔮 FUTURE ROUTES DETAILS:")
    print("=" * 50)
    
    for date in sorted(future_dates):
        records = by_date[date]
        print(f"\n📅 {date} ({len(records)} pickups):")
        print("-" * 40)
        
        # Group by route
        routes = defaultdict(list)
        for record in records:
            truck_num = record.get('truck_number', 'Unknown')
            route_num = record.get('route_number', 'Unknown')
            route_key = f"Route {route_num} (Truck {truck_num})"
            routes[route_key].append(record)
        
        for route_key, pickups in sorted(routes.items()):
            dairy_count = len(set(p.get('producer_name', 'Unknown') for p in pickups))
            
            print(f"  {route_key}:")
            print(f"    📦 {len(pickups)} pickups from {dairy_count} dairies")
            
            # Show status info
            sample = pickups[0]
            has_dropoff = bool(sample.get('dropoff_date'))
            has_geofence = bool(sample.get('geofence_enter_time'))
            
            print(f"    📋 Status indicators:")
            print(f"      - dropoff_date: {'✅ HAS DATA' if has_dropoff else '❌ EMPTY'}")
            print(f"      - geofence_enter_time: {'✅ HAS DATA' if has_geofence else '❌ EMPTY'}")
            
            # Show dairies
            dairy_pickups = defaultdict(list)
            for pickup in pickups:
                dairy = pickup.get('producer_name', 'Unknown')
                tank = pickup.get('producer_tank', 'Unknown')
                dairy_pickups[dairy].append(tank)
            
            for dairy, tanks in dairy_pickups.items():
                tanks_str = ', '.join(map(str, sorted(tanks)))
                print(f"      - {dairy}: tanks {tanks_str}")
            print()
    
    print("\n💡 KEY INSIGHTS:")
    print("-" * 30)
    print("• Future routes should have:")
    print("  - dropoff_date: EMPTY (not delivered yet)")
    print("  - geofence_enter_time: EMPTY (not arrived yet)")
    print("• These should be marked as 'Scheduled' status")
    
    # Check if we're properly detecting scheduled routes
    total_future = sum(len(by_date[date]) for date in future_dates)
    print(f"• Total future pickups for hauler 77: {total_future}")
    
    if total_future > 0:
        print("✅ FUTURE ROUTES EXIST! The issue is in processing logic.")
    else:
        print("❌ NO FUTURE ROUTES - Milk Movement may not provide them far in advance.")

if __name__ == "__main__":
    check_future_routes() 