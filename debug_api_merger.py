#!/usr/bin/env python3
"""
DEBUG SCRIPT: Show exactly what both APIs return and how they should merge
No Docker, no complexity - just raw truth about what's happening
"""

import requests
import json
from datetime import date, datetime, timedelta, timezone
import pandas as pd
import pytz

# API Credentials
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"

def get_mm_routes_today():
    """Get today's routes from Milk Movement API"""
    print("🥛 FETCHING MILK MOVEMENT DATA...")
    
    today = date.today().strftime("%Y-%m-%d")
    
    headers = {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}
    
    routes = []
    
    # Get pickups (active routes)
    print("   📦 Fetching pickups...")
    pickup_url = f"{API_BASE_URL}/pickups/load-summary"
    pickup_params = {"start_date": today, "end_date": today}
    
    try:
        pickup_response = requests.get(pickup_url, headers=headers, params=pickup_params)
        pickup_response.raise_for_status()
        pickup_data = pickup_response.json()
        
        for pickup in pickup_data:
            routes.append({
                'lt_number': pickup.get('invoice_number', ''),
                'dairy': pickup.get('producer_name', ''),
                'status': 'active',  # Pickups are active
                'start_time': pickup.get('pickup_date', ''),
                'driver': pickup.get('driver', 'TBD'),
                'truck': pickup.get('truck_number', 'TBD'),
                'tank': pickup.get('producer_tank', 'TBD'),
                'processor': pickup.get('processor_name', 'TBD'),
                'source': 'MM_PICKUP'
            })
        
        print(f"   ✅ Found {len(pickup_data)} pickups")
        
    except Exception as e:
        print(f"   ❌ Error fetching pickups: {e}")
    
    # Get schedules (future routes) - try schedules endpoint
    print("   📅 Fetching schedules...")
    schedule_url = f"{API_BASE_URL}/schedules"
    schedule_params = {"start_date": today, "end_date": today}
    
    try:
        schedule_response = requests.get(schedule_url, headers=headers, params=schedule_params)
        schedule_response.raise_for_status()
        schedule_data = schedule_response.json()
        
        for schedule in schedule_data:
            routes.append({
                'lt_number': schedule.get('lt_number', ''),
                'dairy': schedule.get('producer_name', ''),
                'status': 'scheduled',
                'start_time': schedule.get('pickup_date', ''),
                'driver': schedule.get('driver', 'TBD'),
                'truck': schedule.get('truck', 'TBD'),
                'tank': schedule.get('tank', 'TBD'),
                'processor': schedule.get('processor', 'TBD'),
                'source': 'MM_SCHEDULE'
            })
        
        print(f"   ✅ Found {len(schedule_data)} schedules")
        
    except Exception as e:
        print(f"   ⚠️  Error fetching schedules: {e}")
    
    print(f"✅ Found {len(routes)} total routes from Milk Movement")
    return routes

def get_samsara_routes_today():
    """Get today's routes from Samsara API"""
    print("🚛 FETCHING SAMSARA DATA...")
    
    url = "https://api.samsara.com/fleet/routes"
    
    # Get today's data in UTC
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
    
    # MST timezone for user display
    mst = pytz.timezone('America/Phoenix')  # Arizona doesn't observe DST
    
    routes = []
    
    for route in data.get('data', []):
        # Extract LT number from route name
        route_name = route.get('name', '')
        lt_number = ''
        
        # Look for pattern like "Route 145: BVW35134"
        import re
        match = re.search(r'([A-Z]{3}\d{5})', route_name)
        if match:
            lt_number = match.group(1)
        
        # Analyze stops to determine status - DAIRY-FOCUSED LOGIC
        stops = route.get('stops', [])
        depot_stop = None
        dairy_stop = None
        
        for i, stop in enumerate(stops):
            stop_name = stop.get('name', '').lower()
            
            # DEPOT LOGIC: First stop OR stop with only departure time (no arrival)
            if i == 0 or (stop.get('scheduledDepartureTime') and not stop.get('scheduledArrivalTime')):
                depot_stop = stop
            # DAIRY LOGIC: Stop with both arrival AND departure times + dairy keywords
            elif (stop.get('scheduledArrivalTime') and stop.get('scheduledDepartureTime') and 
                  any(word in stop_name for word in ['dairy', 'holsteins', 't&k', 'dickman', 'milky', 'triple', 'piazzo', 'belmont'])):
                # Only care about FIRST dairy stop found (ignore processors)
                if dairy_stop is None:
                    dairy_stop = stop
        
        # BUSINESS LOGIC: Only care about route status UP TO DAIRY
        # 1. Scheduled: Route hasn't started
        # 2. En Route: Traveling TO dairy (left depot, not at dairy)  
        # 3. Filling Tank: At dairy loading milk (arrived but not departed)
        # 4. Completed: Left dairy (pickup finished - WE DON'T CARE ABOUT PROCESSORS)
        
        status = "scheduled"
        dairy_arrival_mst = ""
        dairy_departure_mst = ""
        depot_departure_mst = ""
        
        if dairy_stop:
            dairy_state = dairy_stop.get('state', '')
            
            # Convert times to MST for display
            if dairy_stop.get('actualArrivalTime'):
                dairy_arrival_utc = datetime.fromisoformat(dairy_stop['actualArrivalTime'].replace('Z', '+00:00'))
                dairy_arrival_mst = dairy_arrival_utc.astimezone(mst).strftime('%H:%M MST')
            
            if dairy_stop.get('actualDepartureTime'):
                dairy_departure_utc = datetime.fromisoformat(dairy_stop['actualDepartureTime'].replace('Z', '+00:00'))
                dairy_departure_mst = dairy_departure_utc.astimezone(mst).strftime('%H:%M MST')
            
            if depot_stop and depot_stop.get('actualDepartureTime'):
                depot_departure_utc = datetime.fromisoformat(depot_stop['actualDepartureTime'].replace('Z', '+00:00'))
                depot_departure_mst = depot_departure_utc.astimezone(mst).strftime('%H:%M MST')
            
            # Determine status based on DAIRY STOP ONLY
            if dairy_state == 'departed':
                status = "completed"  # ✅ LEFT DAIRY = ROUTE COMPLETE (ignore processors)
            elif dairy_state == 'arrived':
                status = "filling_tank"  # 🥛 AT DAIRY = FILLING TANK
            elif dairy_state == 'skipped':
                # Check if we've left depot (en route to dairy)
                if depot_stop and depot_stop.get('state') == 'departed':
                    status = "en_route"  # 🚛 LEFT DEPOT, TRAVELING TO DAIRY
                else:
                    status = "scheduled"  # 📅 HASN'T STARTED YET
            else:
                # Default logic if state is unclear
                if depot_stop and depot_stop.get('state') == 'departed':
                    status = "en_route"  # 🚛 LEFT DEPOT, TRAVELING TO DAIRY
        
        # Extract dairy name from dairy stop
        dairy_name = "Unknown"
        if dairy_stop:
            dairy_name = dairy_stop.get('name', 'Unknown')
        
        # Get route times (convert to MST)
        actual_start_mst = ""
        actual_end_mst = ""
        
        if route.get('actualRouteStartTime'):
            start_utc = datetime.fromisoformat(route['actualRouteStartTime'].replace('Z', '+00:00'))
            actual_start_mst = start_utc.astimezone(mst).strftime('%H:%M MST')
        
        if route.get('actualRouteEndTime'):
            end_utc = datetime.fromisoformat(route['actualRouteEndTime'].replace('Z', '+00:00'))
            actual_end_mst = end_utc.astimezone(mst).strftime('%H:%M MST')
        
        routes.append({
            'lt_number': lt_number,
            'samsara_id': route.get('id', ''),
            'route_name': route_name,
            'dairy': dairy_name,
            'status': status,
            'actual_start': actual_start_mst,
            'actual_end': actual_end_mst,
            'driver': route.get('driver', {}).get('name', 'TBD'),
            'depot_state': depot_stop.get('state', '') if depot_stop else '',
            'dairy_state': dairy_stop.get('state', '') if dairy_stop else '',
            'dairy_arrival': dairy_arrival_mst,
            'dairy_departure': dairy_departure_mst,
            'depot_departure': depot_departure_mst,
            'source': 'SAMSARA'
        })
    
    print(f"✅ Found {len(routes)} routes from Samsara")
    return routes

def merge_and_compare():
    """Merge both APIs and show the truth"""
    print("\n" + "="*80)
    print("🔍 FETCHING DATA FROM BOTH APIS...")
    print("="*80)
    
    mm_routes = get_mm_routes_today()
    samsara_routes = get_samsara_routes_today()
    
    print(f"\n📊 SUMMARY:")
    print(f"   Milk Movement: {len(mm_routes)} routes")
    print(f"   Samsara: {len(samsara_routes)} routes")
    
    # Create merged data
    merged_data = []
    
    # First, add all MM routes
    for mm_route in mm_routes:
        # Find matching Samsara route
        samsara_match = None
        for samsara_route in samsara_routes:
            if samsara_route['lt_number'] == mm_route['lt_number']:
                samsara_match = samsara_route
                break
        
        merged_data.append({
            'LT_NUMBER': mm_route['lt_number'],
            'DAIRY': mm_route['dairy'],
            'TANK': mm_route['tank'],
            'TRUCK': mm_route['truck'],
            'DRIVER': mm_route['driver'],
            'MM_STATUS': mm_route['status'],
            'SAMSARA_STATUS': samsara_match['status'] if samsara_match else 'NO_MATCH',
            'CORRECT_STATUS': samsara_match['status'] if samsara_match else mm_route['status'],
            'MM_TIME': mm_route['start_time'],
            'SAMSARA_START_MST': samsara_match['actual_start'] if samsara_match else '',
            'SAMSARA_END_MST': samsara_match['actual_end'] if samsara_match else '',
            'DAIRY_ARRIVAL_MST': samsara_match['dairy_arrival'] if samsara_match else '',
            'DAIRY_DEPARTURE_MST': samsara_match['dairy_departure'] if samsara_match else '',
            'DEPOT_DEPARTURE_MST': samsara_match['depot_departure'] if samsara_match else '',
            'MATCH': '✅' if samsara_match else '❌',
            'DAIRY_STATE': samsara_match['dairy_state'] if samsara_match else '',
            'DEPOT_STATE': samsara_match['depot_state'] if samsara_match else ''
        })
    
    # Convert to DataFrame for better display
    df = pd.DataFrame(merged_data)
    
    print(f"\n🎯 MERGED RESULTS ({len(merged_data)} routes):")
    print("="*80)
    
    # Show key routes (T&K, Route 145, etc.)
    key_routes = df[df['DAIRY'].str.contains('T&K', na=False)]
    
    if not key_routes.empty:
        print("\n🔥 T&K ROUTES (Your Problem Routes):")
        print(key_routes[['LT_NUMBER', 'DAIRY', 'TANK', 'TRUCK', 'MM_STATUS', 'SAMSARA_STATUS', 'CORRECT_STATUS', 'MATCH', 'DAIRY_STATE', 'DAIRY_DEPARTURE_MST']].to_string(index=False))
    
    # Show unmatched routes
    unmatched = df[df['MATCH'] == '❌']
    if not unmatched.empty:
        print(f"\n❌ UNMATCHED ROUTES ({len(unmatched)}):")
        print(unmatched[['LT_NUMBER', 'DAIRY', 'MM_STATUS']].head(10).to_string(index=False))
    
    # Show matched routes with status conflicts
    matched = df[df['MATCH'] == '✅']
    conflicts = matched[matched['MM_STATUS'] != matched['SAMSARA_STATUS']]
    if not conflicts.empty:
        print(f"\n⚠️  STATUS CONFLICTS ({len(conflicts)}):")
        print(conflicts[['LT_NUMBER', 'DAIRY', 'MM_STATUS', 'SAMSARA_STATUS', 'CORRECT_STATUS', 'DAIRY_STATE', 'DAIRY_DEPARTURE_MST']].to_string(index=False))
    
    # Show summary stats
    total_routes = len(df)
    matched_routes = len(matched)
    match_rate = (matched_routes / total_routes * 100) if total_routes > 0 else 0
    
    print(f"\n📈 MATCHING STATISTICS:")
    print(f"   Total Routes: {total_routes}")
    print(f"   Matched: {matched_routes} ({match_rate:.1f}%)")
    print(f"   Unmatched: {len(unmatched)}")
    print(f"   Status Conflicts: {len(conflicts)}")
    
    # Show detailed timeline for completed T&K routes
    completed_tk_routes = df[(df['DAIRY'].str.contains('T&K', na=False)) & 
                             (df['SAMSARA_STATUS'] == 'completed')]
    
    if not completed_tk_routes.empty:
        print(f"\n⏰ T&K COMPLETED ROUTES - FULL TIMELINE:")
        for _, route in completed_tk_routes.iterrows():
            print(f"   🚛 {route['LT_NUMBER']} (Tank {route['TANK']}, Truck {route['TRUCK']}):")
            if route['DEPOT_DEPARTURE_MST']:
                print(f"      📍 Left Depot: {route['DEPOT_DEPARTURE_MST']} → En Route")
            if route['DAIRY_ARRIVAL_MST']:
                print(f"      🥛 Arrived Dairy: {route['DAIRY_ARRIVAL_MST']} → Filling Tank")
            if route['DAIRY_DEPARTURE_MST']:
                print(f"      ✅ Left Dairy: {route['DAIRY_DEPARTURE_MST']} → COMPLETED")
            print()
    
    # Save to CSV for analysis
    csv_file = f"route_comparison_{date.today().strftime('%Y%m%d')}.csv"
    df.to_csv(csv_file, index=False)
    print(f"\n💾 Full data saved to: {csv_file}")
    
    return df

if __name__ == "__main__":
    print("🚛🥛 API MERGER DEBUG SCRIPT")
    print("=" * 50)
    
    try:
        results = merge_and_compare()
        
        print(f"\n✅ DONE! Check the CSV file for full details.")
        print("\n🎯 THE TRUTH: This table shows what your app SHOULD be displaying!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc() 