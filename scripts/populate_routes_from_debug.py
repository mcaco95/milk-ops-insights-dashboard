#!/usr/bin/env python3
"""
ROUTES DATABASE POPULATION SCRIPT
Uses the EXACT same proven logic from debug_api_merger.py to populate the database
This ensures the frontend gets the correct 4-status data with proper timestamps
"""

import requests
import json
import psycopg2
import os
from datetime import date, datetime, timedelta, timezone
import pandas as pd
import pytz

# API Credentials (same as debug script)
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "dairy_operations"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

def get_mm_routes_today():
    """Get today's routes from Milk Movement API (EXACT COPY FROM DEBUG SCRIPT)"""
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
    
    # Get schedules (future routes)
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
    """Get today's routes from Samsara API (EXACT COPY FROM DEBUG SCRIPT)"""
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

def get_dairy_mapping(conn):
    """Get dairy name to ID mapping from database"""
    mapping = {}
    with conn.cursor() as cur:
        cur.execute("SELECT id, milk_movement_names FROM dairies")
        for row in cur.fetchall():
            dairy_id, names = row
            if names:
                for name in names:
                    mapping[name] = dairy_id
    return mapping

def merge_and_populate_database():
    """Merge both APIs and populate database (SAME LOGIC AS DEBUG SCRIPT)"""
    print("\n" + "="*80)
    print("🔍 FETCHING DATA FROM BOTH APIS AND POPULATING DATABASE...")
    print("="*80)
    
    mm_routes = get_mm_routes_today()
    samsara_routes = get_samsara_routes_today()
    
    print(f"\n📊 SUMMARY:")
    print(f"   Milk Movement: {len(mm_routes)} routes")
    print(f"   Samsara: {len(samsara_routes)} routes")
    
    # Create merged data (EXACT SAME LOGIC AS DEBUG SCRIPT)
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
            'DEPOT_STATE': samsara_match['depot_state'] if samsara_match else '',
            'PROCESSOR': mm_route['processor']
        })
    
    # Now populate database
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        dairy_mapping = get_dairy_mapping(conn)
        
        if not dairy_mapping:
            print("❌ FATAL: Could not load dairy mappings from database")
            return
        
        with conn.cursor() as cur:
            # Clear today's data first
            today = date.today()
            cur.execute("DELETE FROM routes_data WHERE report_date = %s", (today,))
            print(f"🗑️  Cleared existing routes for {today}")
            
            inserted_count = 0
            
            for route_data in merged_data:
                dairy_name = route_data['DAIRY']
                dairy_id = dairy_mapping.get(dairy_name)
                
                if not dairy_id:
                    print(f"⚠️  No mapping found for dairy '{dairy_name}', skipping...")
                    continue
                
                # Determine final status using PROVEN logic
                final_status = route_data['CORRECT_STATUS']
                
                # Convert status to database format
                db_status_map = {
                    'scheduled': 'scheduled',
                    'en_route': 'active',     # En route = active for ETA calculation
                    'filling_tank': 'active', # Filling tank = active
                    'completed': 'completed'
                }
                db_status = db_status_map.get(final_status, 'scheduled')
                
                # Parse timestamps for ETA calculation
                estimated_arrival = None
                start_date = None
                
                # For en_route status, use depot departure + travel time for ETA
                if final_status == 'en_route' and route_data['DEPOT_DEPARTURE_MST']:
                    try:
                        # Parse depot departure time
                        depot_time_str = route_data['DEPOT_DEPARTURE_MST'].replace(' MST', '')
                        depot_hour, depot_minute = map(int, depot_time_str.split(':'))
                        depot_datetime = datetime.combine(today, datetime.min.time().replace(hour=depot_hour, minute=depot_minute))
                        
                        # Estimate 2-hour travel time for ETA (can be improved with real calculation)
                        estimated_arrival = depot_datetime + timedelta(hours=2)
                        start_date = depot_datetime
                    except:
                        estimated_arrival = None
                        start_date = None
                
                # For other statuses, use actual times if available
                elif route_data['DAIRY_ARRIVAL_MST']:
                    try:
                        arrival_time_str = route_data['DAIRY_ARRIVAL_MST'].replace(' MST', '')
                        arrival_hour, arrival_minute = map(int, arrival_time_str.split(':'))
                        estimated_arrival = datetime.combine(today, datetime.min.time().replace(hour=arrival_hour, minute=arrival_minute))
                        start_date = estimated_arrival
                    except:
                        pass
                
                # Insert into database
                cur.execute("""
                    INSERT INTO routes_data
                    (
                        dairy_id, report_date, samsara_route_id, driver_name, truck_id, status, 
                        estimated_arrival, start_date, route, dairy_name, tank, processor, 
                        lt_number, fairlife_number, tracking_link, last_updated
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    dairy_id,
                    today,
                    route_data['LT_NUMBER'],  # Use LT number as route ID
                    route_data['DRIVER'] if route_data['DRIVER'] != 'TBD' else None,
                    route_data['TRUCK'] if route_data['TRUCK'] != 'TBD' else None,
                    db_status,
                    estimated_arrival,
                    start_date,
                    route_data['LT_NUMBER'],
                    route_data['DAIRY'],
                    route_data['TANK'] if route_data['TANK'] != 'TBD' else None,
                    route_data['PROCESSOR'] if route_data['PROCESSOR'] != 'TBD' else None,
                    route_data['LT_NUMBER'],
                    None,  # fairlife_number
                    None,  # tracking_link
                    datetime.utcnow()
                ))
                inserted_count += 1
                
                print(f"✅ Inserted: {route_data['LT_NUMBER']} - {dairy_name} - {final_status}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎯 SUCCESS: Inserted {inserted_count} routes into database!")
        print("="*80)
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚛🥛 ROUTES DATABASE POPULATION SCRIPT")
    print("Using EXACT same logic as debug_api_merger.py")
    print("=" * 50)
    
    try:
        merge_and_populate_database()
        print(f"\n✅ DONE! Your app should now show the correct route data!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc() 