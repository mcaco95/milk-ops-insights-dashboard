#!/usr/bin/env python3
"""
Debug raw Samsara timestamps to identify timezone conversion issues
"""

import requests
import re
import pytz
from datetime import datetime, timezone, timedelta

SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

def debug_raw_timestamps():
    """Show raw Samsara timestamps vs converted times"""
    print("🕐 RAW TIMESTAMP DEBUG")
    print("=" * 50)
    
    # Current time info
    mst = pytz.timezone('America/Phoenix')
    utc_now = datetime.now(timezone.utc)
    mst_now = utc_now.astimezone(mst)
    
    print(f"Current UTC: {utc_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print(f"Current MST: {mst_now.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    print()
    
    # Use FIXED timezone logic for API call
    mst_today = mst_now.replace(hour=0, minute=0, second=0, microsecond=0)
    mst_tomorrow = mst_today + timedelta(days=1)
    start_utc = mst_today.astimezone(timezone.utc)
    end_utc = mst_tomorrow.astimezone(timezone.utc)
    
    url = "https://api.samsara.com/fleet/routes"
    headers = {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}
    params = {
        "startTime": start_utc.isoformat(),
        "endTime": end_utc.isoformat(),
        "limit": 500
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        routes = data.get('data', [])
        print(f"Found {len(routes)} routes")
        print()
        
        # Find routes with actual timestamps
        for route in routes[:10]:
            route_name = route.get('name', '')
            
            # Extract LT number
            lt_match = re.search(r'([A-Z]{3}\d{5})', route_name)
            lt_number = lt_match.group(1) if lt_match else 'NO_LT'
            
            # Find dairy stop with timestamps
            stops = route.get('stops', [])
            for stop in stops:
                stop_name = stop.get('name', '').lower()
                
                # Look for dairy stops
                if any(word in stop_name for word in ['dairy', 'holsteins', 't&k', 'dickman', 'milky', 'triple']):
                    arrival_raw = stop.get('actualArrivalTime', '')
                    departure_raw = stop.get('actualDepartureTime', '')
                    
                    if arrival_raw or departure_raw:
                        print(f"🚛 {lt_number} - {route_name[:50]}...")
                        print(f"   Dairy Stop: {stop.get('name', '')}")
                        print(f"   State: {stop.get('state', '')}")
                        print()
                        
                        if arrival_raw:
                            print(f"   📍 RAW ARRIVAL: {arrival_raw}")
                            try:
                                # Parse as UTC
                                arrival_utc = datetime.fromisoformat(arrival_raw.replace('Z', '+00:00'))
                                arrival_mst = arrival_utc.astimezone(mst)
                                print(f"   📍 CONVERTED:   {arrival_mst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                                
                                # Show if this is past/future
                                if arrival_mst > mst_now:
                                    diff = arrival_mst - mst_now
                                    print(f"   ⚠️  FUTURE:     {diff.total_seconds()/3600:.1f} hours from now!")
                                else:
                                    diff = mst_now - arrival_mst
                                    print(f"   ✅ PAST:       {diff.total_seconds()/3600:.1f} hours ago")
                            except Exception as e:
                                print(f"   ❌ PARSE ERROR: {e}")
                        
                        if departure_raw:
                            print(f"   🚪 RAW DEPARTURE: {departure_raw}")
                            try:
                                departure_utc = datetime.fromisoformat(departure_raw.replace('Z', '+00:00'))
                                departure_mst = departure_utc.astimezone(mst)
                                print(f"   🚪 CONVERTED:    {departure_mst.strftime('%Y-%m-%d %H:%M:%S %Z')}")
                                
                                if departure_mst > mst_now:
                                    diff = departure_mst - mst_now
                                    print(f"   ⚠️  FUTURE:      {diff.total_seconds()/3600:.1f} hours from now!")
                                else:
                                    diff = mst_now - departure_mst
                                    print(f"   ✅ PAST:        {diff.total_seconds()/3600:.1f} hours ago")
                            except Exception as e:
                                print(f"   ❌ PARSE ERROR: {e}")
                        
                        print("=" * 60)
                        print()
                        break
    
    except Exception as e:
        print(f"❌ API Error: {e}")

if __name__ == "__main__":
    debug_raw_timestamps() 