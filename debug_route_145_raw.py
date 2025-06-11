#!/usr/bin/env python3
"""
Debug script to dump raw Samsara JSON for Route 145 (BVW35134)
"""

import requests
import json
from datetime import datetime, timedelta, timezone
import pytz

# API Credentials
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

def debug_route_145():
    """Get raw Samsara data specifically for Route 145"""
    print("🔍 DEBUGGING ROUTE 145 (BVW35134)")
    print("="*50)
    
    url = "https://api.samsara.com/fleet/routes"
    
    # Get today's data
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    
    params = {
        "startTime": today.isoformat(),
        "endTime": tomorrow.isoformat(),
        "limit": 500
    }
    
    headers = {
        "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    # Find Route 145 (BVW35134)
    route_145 = None
    for route in data.get('data', []):
        route_name = route.get('name', '')
        if 'BVW35134' in route_name:
            route_145 = route
            break
    
    if not route_145:
        print("❌ Route 145 (BVW35134) not found!")
        return
    
    print(f"✅ Found Route 145: {route_145.get('name', 'Unknown')}")
    print(f"📍 Route ID: {route_145.get('id', 'Unknown')}")
    print(f"👨‍✈️ Driver: {route_145.get('driver', {}).get('name', 'Unknown')}")
    
    # Show route-level times
    print(f"\n⏰ ROUTE-LEVEL TIMES:")
    print(f"   Scheduled Start: {route_145.get('scheduledRouteStartTime', 'None')}")
    print(f"   Scheduled End: {route_145.get('scheduledRouteEndTime', 'None')}")
    print(f"   Actual Start: {route_145.get('actualRouteStartTime', 'None')}")
    print(f"   Actual End: {route_145.get('actualRouteEndTime', 'None')}")
    
    # Analyze stops in detail
    stops = route_145.get('stops', [])
    print(f"\n🛑 STOPS BREAKDOWN ({len(stops)} stops):")
    
    mst = pytz.timezone('America/Phoenix')
    
    for i, stop in enumerate(stops):
        stop_name = stop.get('name', 'Unknown')
        stop_state = stop.get('state', 'Unknown')
        
        print(f"\n   Stop {i+1}: {stop_name}")
        print(f"   State: {stop_state}")
        print(f"   Address ID: {stop.get('address', {}).get('id', 'None')}")
        
        # Show all time fields
        time_fields = [
            'scheduledArrivalTime', 
            'scheduledDepartureTime',
            'actualArrivalTime',
            'actualDepartureTime',
            'enRouteTime',
            'skippedTime'
        ]
        
        for field in time_fields:
            if stop.get(field):
                utc_time = datetime.fromisoformat(stop[field].replace('Z', '+00:00'))
                mst_time = utc_time.astimezone(mst).strftime('%H:%M MST')
                print(f"   {field}: {stop[field]} → {mst_time}")
        
        # Classify stop type
        stop_name_lower = stop_name.lower()
        if 'uda' in stop_name_lower or 'depot' in stop_name_lower or 'office' in stop_name_lower:
            print(f"   🏢 DEPOT STOP")
        elif any(word in stop_name_lower for word in ['dairy', 'holsteins', 't&k']):
            print(f"   🥛 DAIRY STOP")
        else:
            print(f"   📦 OTHER STOP (likely processor)")
    
    # Show raw JSON for complete analysis
    print(f"\n📄 COMPLETE RAW JSON:")
    print("="*50)
    print(json.dumps(route_145, indent=2))

if __name__ == "__main__":
    debug_route_145() 