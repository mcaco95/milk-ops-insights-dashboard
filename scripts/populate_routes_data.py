#!/usr/bin/env python3
"""
ROUTES DATABASE POPULATION SCRIPT (DOCKER VERSION)
Uses the EXACT same proven logic from debug_api_merger.py to populate the database
This ensures the frontend gets the correct 4-status data with proper timestamps
Designed to run in Docker scheduler
"""

import requests
import json
import psycopg2
import os
import sys
from datetime import date, datetime, timedelta, timezone
import pandas as pd
import pytz
import re

# API Credentials
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
TOMTOM_API_KEY = "s4SRO0ZMWIrxsaAsUrIRLN4R5MZHabTt"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"

# Database configuration (Docker environment)
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "dairy_operations"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

# Route number to dairy mapping based on team's list
ROUTE_DAIRY_MAPPING = {
    # Routes 1-29: Milky Way
    **{i: "Milky Way Dairy (633)" for i in range(1, 30)},
    # Route 36: D&I Dairy 805
    36: "D&I Dairy (805)",
    # Routes 40, 43-48: Triple G
    40: "Triple G Dairy",
    **{i: "Triple G Dairy" for i in range(43, 49)},
    # Routes 41-42: Belmont
    41: "Belmont Dairy(701)",
    42: "Belmont Dairy(701)",
    # Routes 49, 56-60: Belmont
    49: "Belmont Dairy(701)",
    **{i: "Belmont Dairy(701)" for i in range(56, 61)},
    # Routes 74-80: Dickman
    **{i: "Dickman and Sons Dairy (815)" for i in range(74, 81)},
    # Routes 81-82: Triple G
    81: "Triple G Dairy",
    82: "Triple G Dairy",
    # Routes 90-99: D&I Holstein 716
    **{i: "D&I Holsteins (716)" for i in range(90, 100)},
    # Routes 114, 118: Triple G
    114: "Triple G Dairy",
    118: "Triple G Dairy",
    # Route 119: D&I Holstein
    119: "D&I Holsteins (716)",
    # Route 120: Triple G
    120: "Triple G Dairy",
    # Routes 122-185: T&K
    **{i: "T&K" for i in range(122, 186)},
    # Routes 330-339: Arizona Dairy
    **{i: "Arizona Dairy" for i in range(330, 340)},
    # Routes 340-343: Piazzo Dairy
    340: "Piazzo Dairy (800)",
    341: "Piazzo Dairy (800)", 
    342: "Piazzo Dairy (800)",
    343: "Piazzo Dairy (800)",
}

# Reverse mapping to get route number from dairy name
DAIRY_TO_ROUTE_MAPPING = {}
for route_num, dairy_name in ROUTE_DAIRY_MAPPING.items():
    if dairy_name not in DAIRY_TO_ROUTE_MAPPING:
        DAIRY_TO_ROUTE_MAPPING[dairy_name] = []
    DAIRY_TO_ROUTE_MAPPING[dairy_name].append(route_num)

def get_mm_routes_today():
    """Get today's AND tomorrow's routes from Milk Movement API"""
    print("🥛 FETCHING MILK MOVEMENT DATA...")
    
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    headers = {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}
    
    routes = []
    
    # Get routes for TODAY and TOMORROW
    for target_date in [today, tomorrow]:
        date_str = target_date.strftime("%Y-%m-%d")
        print(f"   📅 Fetching for {date_str}...")
        
        # Get pickups (active routes)
        print(f"   📦 Fetching pickups for {date_str}...")
        pickup_url = f"{API_BASE_URL}/pickups/load-summary"
        pickup_params = {"start_date": date_str, "end_date": date_str}
        
        try:
            pickup_response = requests.get(pickup_url, headers=headers, params=pickup_params)
            pickup_response.raise_for_status()
            pickup_data = pickup_response.json()
            
            # Filter by hauler 77 only
            hauler_77_pickups = [p for p in pickup_data if p.get('hauler_number') == 77]
            
            for pickup in hauler_77_pickups:
                # Extract route number and Fairlife number
                route_number = pickup.get('route_number', '')
                fairlife_number = None
                
                # Try to extract Fairlife number from processor info
                processor_name = pickup.get('processor_name', '')
                processor_number = pickup.get('processor_number', '')
                
                # Generate Fairlife number if processor is Fairlife
                if 'fairlife' in processor_name.lower():
                    fairlife_number = f"10{processor_number}{pickup.get('producer_number', '')}"
                
                routes.append({
                    'lt_number': pickup.get('invoice_number', ''),
                    'route_number': route_number,
                    'dairy': pickup.get('producer_name', ''),
                    'status': 'active',  # Pickups are active
                    'start_time': pickup.get('pickup_date', ''),
                    'driver': pickup.get('driver', 'TBD'),
                    'truck': pickup.get('truck_number', 'TBD'),
                    'tank': pickup.get('producer_tank', 'TBD'),
                    'processor': f"{processor_name} - {processor_number}" if processor_number else processor_name,
                    'fairlife_number': fairlife_number,
                    'source': 'MM_PICKUP',
                    'route_date': target_date
                })
            
            print(f"   ✅ Found {len(hauler_77_pickups)} hauler 77 pickups for {date_str} (filtered from {len(pickup_data)} total)")
            
        except Exception as e:
            print(f"   ❌ Error fetching pickups for {date_str}: {e}")
        
        # Get schedules (future routes)
        print(f"   📅 Fetching schedules for {date_str}...")
        schedule_url = f"{API_BASE_URL}/schedules"
        schedule_params = {"start_date": date_str, "end_date": date_str}
        
        try:
            schedule_response = requests.get(schedule_url, headers=headers, params=schedule_params)
            schedule_response.raise_for_status()
            schedule_data = schedule_response.json()
            
            # Filter by hauler 77 only - FIXED: Use nested hauler object
            hauler_77_schedules = [s for s in schedule_data if s.get('hauler', {}).get('hauler_number') == '77']
            
            for schedule in hauler_77_schedules:
                # Get dairy name from route number using mapping
                dairy_name = 'Unknown'
                route_name = schedule.get('route_name', '')
                route_number = route_name  # Store the actual route number
                
                # SKIP invalid route names to prevent "Unknown Route ()" entries
                if not route_name or not route_name.strip():
                    print(f"   ⚠️  Skipping schedule with empty route_name: {schedule.get('lt_number', 'NO_LT')}")
                    continue
                
                try:
                    route_num = int(route_name)
                    dairy_name = ROUTE_DAIRY_MAPPING.get(route_num, f'Unknown Route {route_num}')
                except (ValueError, TypeError):
                    # If route_name is not a number, keep as Unknown
                    dairy_name = f'Unknown Route ({route_name})'
                
                # Extract processor info
                processor_info = schedule.get('destination_processor', {})
                processor_name = processor_info.get('name', 'TBD')
                processor_license = processor_info.get('license_number', '')
                processor_display = f"{processor_name} - {processor_license}" if processor_license else processor_name
                
                # Generate Fairlife number if applicable
                fairlife_number = None
                if 'fairlife' in processor_name.lower() or processor_license == '40':
                    # Use route number and amount for Fairlife number generation
                    fairlife_number = f"10{processor_license}{route_name}"
                
                routes.append({
                    'lt_number': schedule.get('lt_number', ''),
                    'route_number': route_number,
                    'dairy': dairy_name,
                    'status': 'scheduled',
                    'start_time': schedule.get('start_date', ''),
                    'driver': schedule.get('driver', 'TBD'),
                    'truck': schedule.get('truck', 'TBD'),
                    'tank': schedule.get('tank', 'TBD'),
                    'processor': processor_display,
                    'fairlife_number': fairlife_number,
                    'source': 'MM_SCHEDULE',
                    'route_date': target_date
                })
            
            print(f"   ✅ Found {len(hauler_77_schedules)} hauler 77 schedules for {date_str} (filtered from {len(schedule_data)} total)")
            
        except Exception as e:
            print(f"   ⚠️  Error fetching schedules for {date_str}: {e}")
    
    print(f"✅ Found {len(routes)} total routes from Milk Movement (today + tomorrow)")
    return routes

def get_samsara_routes():
    """Get Samsara routes using FIXED timezone logic"""
    
    # FIXED: Use MST business logic, then convert to UTC for API
    mst = pytz.timezone('America/Phoenix')
    utc_now = datetime.now(timezone.utc)
    mst_now = utc_now.astimezone(mst)
    
    # MST business day: midnight to midnight MST
    mst_today = mst_now.replace(hour=0, minute=0, second=0, microsecond=0)
    mst_tomorrow = mst_today + timedelta(days=1)
    
    # Convert MST business day to UTC for Samsara API
    start_utc = mst_today.astimezone(timezone.utc)
    end_utc = mst_tomorrow.astimezone(timezone.utc)
    
    print(f"📅 MST Business Day: {mst_today.strftime('%Y-%m-%d %H:%M %Z')} to {mst_tomorrow.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"📅 UTC API Range: {start_utc.isoformat()} to {end_utc.isoformat()}")

    url = "https://api.samsara.com/fleet/routes"
    
    headers = {
        "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
        "Accept": "application/json"
    }
    
    response = requests.get(url, params={"startTime": start_utc.isoformat(), "endTime": end_utc.isoformat(), "limit": 500}, headers=headers)
    data = response.json()
    
    # MST timezone for user display
    mst = pytz.timezone('America/Phoenix')  # Arizona doesn't observe DST
    
    routes = []
    
    for route in data.get('data', []):
        # Extract LT number from route name
        route_name = route.get('name', '')
        lt_number = ''
        samsara_tank = None
        
        # Look for pattern like "Route 145: BVW35134"
        match = re.search(r'([A-Z]{3}\d{5})', route_name)
        if match:
            lt_number = match.group(1)
        
        # Extract tank number from route name like "Tank 2" or "Tank 1"
        tank_match = re.search(r'[Tt]ank\s*(\d+)', route_name)
        if tank_match:
            samsara_tank = tank_match.group(1)
        
        # Analyze stops to determine status - ENHANCED TIMESTAMP-BASED LOGIC
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
        
        # Extract timestamps in MST for display AND UTC for status logic
        status = "scheduled"
        dairy_arrival_mst = ""
        dairy_departure_mst = ""
        depot_departure_mst = ""
        
        # Raw timestamp data for status determination
        dairy_arrival_utc = None
        dairy_departure_utc = None
        depot_departure_utc = None
        
        if dairy_stop:
            # Convert times to MST for display
            if dairy_stop.get('actualArrivalTime'):
                arrival_utc = datetime.fromisoformat(dairy_stop['actualArrivalTime'].replace('Z', '+00:00'))
                dairy_arrival_mst = arrival_utc.astimezone(mst).strftime('%H:%M MST')
                dairy_arrival_utc = arrival_utc  # Store for status logic
            
            if dairy_stop.get('actualDepartureTime'):
                departure_utc = datetime.fromisoformat(dairy_stop['actualDepartureTime'].replace('Z', '+00:00'))
                dairy_departure_mst = departure_utc.astimezone(mst).strftime('%H:%M MST')
                dairy_departure_utc = departure_utc  # Store for status logic
            
            if depot_stop and depot_stop.get('actualDepartureTime'):
                depot_dep_utc = datetime.fromisoformat(depot_stop['actualDepartureTime'].replace('Z', '+00:00'))
                depot_departure_mst = depot_dep_utc.astimezone(mst).strftime('%H:%M MST')
                depot_departure_utc = depot_dep_utc  # Store for status logic
        
        # ENHANCED STATUS DETERMINATION: Timestamps First, then Fallback
        # Priority 1: Use timestamps (most reliable)
        if dairy_departure_utc:
            status = "completed"        # ✅ LEFT DAIRY = ROUTE COMPLETE
        elif dairy_arrival_utc:
            status = "filling_tank"     # 🥛 AT DAIRY = FILLING TANK
        elif depot_departure_utc:
            status = "en_route"         # 🚛 LEFT DEPOT = EN ROUTE TO DAIRY
        else:
            status = "scheduled"        # 📅 HASN'T STARTED YET
        
        # Priority 2: Stale ETA Detection (geofence failure handling)
        if status == "en_route" and depot_departure_utc:
            current_time_utc = datetime.now(timezone.utc)
            route_duration_minutes = (current_time_utc - depot_departure_utc).total_seconds() / 60
            
            # Calculate ETA to detect stale status
            estimated_travel_time = timedelta(hours=2)  # Default travel time
            eta_utc = depot_departure_utc + estimated_travel_time
            eta_minutes_remaining = (eta_utc - current_time_utc).total_seconds() / 60
            
            # STALE ETA DETECTION: If ETA shows "arriving soon" for too long
            if eta_minutes_remaining <= 3 and route_duration_minutes >= 80:  # 2+ hours en route
                status = "completed"  # Auto-correct geofence failure
                print(f"🔧 Auto-corrected {lt_number}: Stale ETA detected (en route {route_duration_minutes:.0f} min)")
        
        # Priority 3: Fallback to state-based logic (legacy support)
        if status == "scheduled" and dairy_stop:
            dairy_state = dairy_stop.get('state', '')
            
            if dairy_state == 'departed':
                status = "completed"
            elif dairy_state == 'arrived':
                status = "filling_tank"  
            elif dairy_state == 'skipped':
                if depot_stop and depot_stop.get('state') == 'departed':
                    status = "en_route"
        
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
            'vehicle_id': route.get('vehicle', {}).get('id', ''),
            'vehicle_name': route.get('vehicle', {}).get('name', 'TBD'),
            'depot_state': depot_stop.get('state', '') if depot_stop else '',
            'dairy_state': dairy_stop.get('state', '') if dairy_stop else '',
            'dairy_arrival': dairy_arrival_mst,
            'dairy_departure': dairy_departure_mst,
            'depot_departure': depot_departure_mst,
            'source': 'SAMSARA',
            'samsara_tank': samsara_tank
        })
    
    print(f"✅ Found {len(routes)} routes from Samsara")
    return routes

def get_dairy_mapping(conn):
    """Get dairy name to ID mapping from database using EXACT same logic as volume script"""
    mapping = {}
    with conn.cursor() as cur:
        cur.execute("SELECT id, milk_movement_names FROM dairies")
        for row in cur.fetchall():
            dairy_id, names = row
            if names:
                for name in names:
                    # Use EXACT names from database - no normalization needed!
                    mapping[name] = dairy_id
    return mapping

def normalize_dairy_name(dairy_name):
    """
    SIMPLIFIED: No complex normalization - just clean basic formatting.
    Real mapping happens via exact string matching in get_dairy_mapping()
    """
    if not dairy_name:
        return dairy_name
    
    # Just basic cleanup, but keep the name mostly intact for exact matching
    return dairy_name.strip()

def populate_routes_data(target_date=None):
    """Main function to populate routes data from both MM and Samsara APIs"""
    print("🔄 STARTING ROUTE DATA POPULATION...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get today's date for reporting
        if target_date:
            report_date = target_date
        else:
            # Use MST for business logic
            mst = pytz.timezone('America/Phoenix')
            mst_now = datetime.now(timezone.utc).astimezone(mst)
            report_date = mst_now.date()
        
        print(f"📅 Processing routes for: {report_date}")
        
        # Clear existing data for today
        delete_query = """
        DELETE FROM routes_data 
        WHERE report_date = %s
        """
        cursor.execute(delete_query, (report_date,))
        print(f"🗑️  Cleared {cursor.rowcount} existing routes for {report_date}")
        
        # Get dairy mappings
        dairy_mappings = get_dairy_mapping(conn)
        
        # Load locations for TomTom ETA calculations
        locations = get_locations_from_db(conn)
        depot_coords = locations.get('depot')
        
        # Get data from both APIs
        mm_routes = get_mm_routes_today()
        samsara_routes = get_samsara_routes()
        
        print(f"\n📊 SUMMARY:")
        print(f"   MM Routes: {len(mm_routes)}")
        print(f"   Samsara Routes: {len(samsara_routes)}")
        
        # ENHANCED: Process and merge data with better status determination
        merged_routes = []
        
        # FIXED: Process each MM route and enhance with Samsara data (not the other way around!)
        # This ensures ALL scheduled routes are preserved, not just active ones
        for mm_route in mm_routes:
            lt_number = mm_route['lt_number']
            
            # Skip routes without LT numbers
            if not lt_number or lt_number == 'NO_LT':
                print(f"⚠️  Skipping MM route without LT number: {mm_route.get('dairy', 'Unknown')}")
                continue
            
            # Find matching Samsara route by LT number
            samsara_match = None
            for samsara_route in samsara_routes:
                if samsara_route['lt_number'] == lt_number:
                    samsara_match = samsara_route
                    break
            
            # Determine final status: Use Samsara if available, otherwise keep MM scheduled status
            if samsara_match:
                # Use real-time Samsara status and timestamps
                final_status = samsara_match['status']
                driver_name = samsara_match['driver']
                samsara_route_id = samsara_match['samsara_id']
                samsara_route_name = samsara_match['route_name']
                samsara_tank = samsara_match['samsara_tank']
                
                # Parse Samsara timestamps
                depot_departure_utc = None
                dairy_arrival_utc = None
                dairy_departure_utc = None
                
                mst = pytz.timezone('America/Phoenix')
                
                # Store depot departure time if available
                if samsara_match['depot_departure']:
                    try:
                        departure_str = samsara_match['depot_departure'].replace(' MST', '')
                        # FIXED: Parse time properly with MST timezone
                        hour, minute = map(int, departure_str.split(':'))
                        # Create MST datetime for today
                        mst_today = datetime.now(mst).replace(hour=hour, minute=minute, second=0, microsecond=0)
                        depot_departure_utc = mst_today.astimezone(timezone.utc)
                    except Exception as e:
                        print(f"⚠️  Error parsing depot departure for {lt_number}: {e}")
                
                # Store dairy arrival time if available
                if samsara_match['dairy_arrival']:
                    try:
                        arrival_str = samsara_match['dairy_arrival'].replace(' MST', '')
                        # FIXED: Parse time properly with MST timezone
                        hour, minute = map(int, arrival_str.split(':'))
                        # Create MST datetime for today
                        mst_today = datetime.now(mst).replace(hour=hour, minute=minute, second=0, microsecond=0)
                        dairy_arrival_utc = mst_today.astimezone(timezone.utc)
                    except Exception as e:
                        print(f"⚠️  Error parsing dairy arrival for {lt_number}: {e}")
                
                # Store dairy departure time if available  
                if samsara_match['dairy_departure']:
                    try:
                        departure_str = samsara_match['dairy_departure'].replace(' MST', '')
                        # FIXED: Parse time properly with MST timezone
                        hour, minute = map(int, departure_str.split(':'))
                        # Create MST datetime for today
                        mst_today = datetime.now(mst).replace(hour=hour, minute=minute, second=0, microsecond=0)
                        dairy_departure_utc = mst_today.astimezone(timezone.utc)
                    except Exception as e:
                        print(f"⚠️  Error parsing dairy departure for {lt_number}: {e}")
                
            else:
                # No Samsara match - keep as scheduled with MM data
                final_status = 'scheduled'
                driver_name = mm_route['driver']
                samsara_route_id = ''
                samsara_route_name = ''
                samsara_tank = ''
                depot_departure_utc = None
                dairy_arrival_utc = None
                dairy_departure_utc = None
            
            # ENHANCED: Calculate ETA using TomTom API for real traffic-aware ETAs
            estimated_eta_utc = None
            if final_status == 'en_route' and depot_departure_utc and depot_coords:
                # Find dairy coordinates
                dairy_coords = find_dairy_coordinates(mm_route['dairy'], locations)
                
                if dairy_coords:
                    # ENHANCED: Get truck's current location for accurate ETA
                    truck_number = mm_route.get('truck', 'TBD')
                    vehicle_id = None
                    vehicle_name = None
                    
                    # Use Samsara vehicle info if available (more reliable)
                    if samsara_match:
                        vehicle_id = samsara_match.get('vehicle_id', '')
                        vehicle_name = samsara_match.get('vehicle_name', 'TBD')
                        if vehicle_name != 'TBD':
                            truck_number = vehicle_name
                        print(f"   🚛 Using Samsara vehicle: ID={vehicle_id}, Name={vehicle_name}")
                    else:
                        print(f"   🚛 Using MM truck number: {truck_number}")
                    
                    # Try to get truck location (try vehicle_id first, then truck_number)
                    truck_location = None
                    if vehicle_id:
                        truck_location = get_vehicle_location_by_id(vehicle_id)
                    
                    if not truck_location and truck_number != 'TBD':
                        truck_location = get_vehicle_location(truck_number)
                    
                    if truck_location:
                        # Use truck's current location → dairy for most accurate ETA
                        print(f"   🗺️  Calculating TomTom ETA for {lt_number} from truck {truck_number} current location to {mm_route['dairy']}")
                        eta_minutes = get_live_eta(truck_location, dairy_coords)
                        
                        if eta_minutes:
                            # ETA = current time + TomTom travel time from current location
                            current_time_utc = datetime.now(timezone.utc)
                            estimated_eta_utc = current_time_utc + timedelta(minutes=eta_minutes)
                            print(f"   ✅ TomTom ETA from current location: {eta_minutes:.0f} minutes")
                        else:
                            # Fallback: depot → dairy if truck location fails
                            print(f"   ⚠️  TomTom failed from truck location, trying depot → dairy")
                            eta_minutes = get_live_eta(depot_coords, dairy_coords)
                            if eta_minutes:
                                estimated_eta_utc = depot_departure_utc + timedelta(minutes=eta_minutes)
                                print(f"   ✅ TomTom ETA from depot: {eta_minutes:.0f} minutes")
                            else:
                                estimated_eta_utc = depot_departure_utc + timedelta(hours=1)
                                print(f"   ⚠️  All TomTom calls failed, using 1-hour fallback")
                    else:
                        # Fallback: depot → dairy if no truck location
                        print(f"   🗺️  No truck location, calculating depot → dairy for {lt_number}")
                        eta_minutes = get_live_eta(depot_coords, dairy_coords)
                        
                        if eta_minutes:
                            estimated_eta_utc = depot_departure_utc + timedelta(minutes=eta_minutes)
                            print(f"   ✅ TomTom ETA from depot: {eta_minutes:.0f} minutes")
                        else:
                            estimated_eta_utc = depot_departure_utc + timedelta(hours=1)
                            print(f"   ⚠️  TomTom failed, using 1-hour fallback")
                else:
                    # Fallback if no dairy coordinates found
                    estimated_eta_utc = depot_departure_utc + timedelta(hours=1)
                    print(f"   ⚠️  No coordinates for {mm_route['dairy']}, using 1-hour fallback")
                    
            elif final_status == 'filling_tank' and dairy_arrival_utc:
                # FILLING_TANK: ETA shows when they arrived (for "Arrived at X" display)
                estimated_eta_utc = dairy_arrival_utc
            elif final_status == 'completed' and dairy_departure_utc:
                # COMPLETED: ETA shows when they left (for "Left at X" display)  
                estimated_eta_utc = dairy_departure_utc
            else:
                # SCHEDULED or fallback cases
                estimated_eta_utc = None
            
            # Use MM data for core route information
            route_number = mm_route['route_number']
            processor = mm_route['processor'] 
            fairlife_number = mm_route['fairlife_number']
            
            # FIXED: Use MM start_time for start_date field (scheduled start time)
            mm_start_date_utc = None
            mm_start_time = mm_route.get('start_time', '')
            if mm_start_time and mm_start_time != 'TBD':
                try:
                    # Parse MM start date/time and convert to UTC for start_date field
                    mm_start_datetime = datetime.fromisoformat(mm_start_time.replace('Z', '+00:00'))
                    mm_start_date_utc = mm_start_datetime.astimezone(timezone.utc)
                except Exception as e:
                    print(f"⚠️  Error parsing MM start time for {lt_number}: {e}")
                    mm_start_date_utc = None
            
            # Try to map dairy name to our dairy ID using EXACT matching (like volume script)
            dairy_name_raw = mm_route['dairy']
            dairy_id = dairy_mappings.get(dairy_name_raw, None)
            
            if not dairy_id:
                print(f"⚠️  Skipping route - no dairy mapping found:")
                print(f"      Raw: '{dairy_name_raw}' (exact match required)")
                continue
            
            # Create enhanced route entry with all timestamp data
            merged_route = {
                'dairy_id': dairy_id,
                'samsara_route_id': samsara_route_id,
                'samsara_route_name': samsara_route_name,  # STORE FULL ROUTE NAME
                'report_date': report_date,
                'driver_name': driver_name,
                'truck_id': '',  # Not available in current data
                'status': final_status,
                
                # ENHANCED: Separate timestamp fields
                'depot_departure_time': depot_departure_utc,
                'dairy_arrival_time': dairy_arrival_utc,
                'dairy_departure_time': dairy_departure_utc,
                'estimated_eta': estimated_eta_utc,
                
                # Legacy fields (for backwards compatibility)
                'estimated_arrival': estimated_eta_utc,  # Use ETA for legacy field
                'start_date': mm_start_date_utc or depot_departure_utc,  # Use MM start time, fallback to depot departure
                
                'route': route_number,
                'dairy_name': dairy_name_raw,
                'tank': mm_route['tank'],  # Use MM tank data
                'samsara_tank': samsara_tank,  # Tank info from Samsara route name
                'processor': processor,
                'lt_number': lt_number,
                'fairlife_number': fairlife_number,
                'tracking_link': f"https://cloud.samsara.com/o/1234/fleet/routes/{samsara_route_id}" if samsara_route_id else None
            }
            
            merged_routes.append(merged_route)
        
        # Insert merged routes into database with ENHANCED fields
        insert_query = """
        INSERT INTO routes_data (
            dairy_id, samsara_route_id, samsara_route_name, report_date, driver_name, truck_id,
            status, depot_departure_time, dairy_arrival_time, dairy_departure_time, estimated_eta,
            estimated_arrival, start_date, route, dairy_name, tank,
            samsara_tank, processor, lt_number, fairlife_number, tracking_link
        ) VALUES (
            %(dairy_id)s, %(samsara_route_id)s, %(samsara_route_name)s, %(report_date)s, %(driver_name)s, %(truck_id)s,
            %(status)s, %(depot_departure_time)s, %(dairy_arrival_time)s, %(dairy_departure_time)s, %(estimated_eta)s,
            %(estimated_arrival)s, %(start_date)s, %(route)s, %(dairy_name)s, %(tank)s,
            %(samsara_tank)s, %(processor)s, %(lt_number)s, %(fairlife_number)s, %(tracking_link)s
        )
        """
        
        cursor.executemany(insert_query, merged_routes)
        conn.commit()
        
        print(f"\n✅ SUCCESS: Inserted {len(merged_routes)} routes into database")
        print(f"   Scheduled: {sum(1 for r in merged_routes if r['status'] == 'scheduled')}")
        print(f"   En Route: {sum(1 for r in merged_routes if r['status'] == 'en_route')}")
        print(f"   Filling Tank: {sum(1 for r in merged_routes if r['status'] == 'filling_tank')}")
        print(f"   Completed: {sum(1 for r in merged_routes if r['status'] == 'completed')}")
        print(f"   With Tank Info: {sum(1 for r in merged_routes if r['samsara_tank'])}")
        
    except Exception as e:
        print(f"❌ ERROR in populate_routes_data: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

def get_live_eta(origin_coords, dest_coords):
    """
    Gets a traffic-aware ETA from the TomTom API.
    Returns the ETA in minutes.
    """
    if not origin_coords or not dest_coords:
        return None
    
    origin_str = f"{origin_coords['lat']},{origin_coords['lon']}"
    dest_str = f"{dest_coords['lat']},{dest_coords['lon']}"
    
    url = f"https://api.tomtom.com/routing/1/calculateRoute/{origin_str}:{dest_str}/json"
    params = {"key": TOMTOM_API_KEY, "traffic": "true"}
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        travel_time_seconds = data['routes'][0]['summary']['travelTimeInSeconds']
        return travel_time_seconds / 60
    except (requests.exceptions.RequestException, IndexError, KeyError):
        return None

def get_locations_from_db(conn):
    """Get dairy and depot coordinates from database for TomTom ETA calculations"""
    locations = {}
    try:
        with conn.cursor() as cur:
            # Get depot location (hardcoded for now - you can add to database later)
            locations['depot'] = {"lat": 33.4484, "lon": -112.0740}  # Phoenix depot coordinates
            
            # Get dairy locations from samsara_addresses table
            cur.execute("SELECT name, latitude, longitude FROM samsara_addresses WHERE latitude IS NOT NULL AND longitude IS NOT NULL")
            addresses = cur.fetchall()
            
            for name, lat, lon in addresses:
                if name and name.strip():
                    locations[name.lower()] = {"lat": float(lat), "lon": float(lon)}
            
            print(f"   📍 Loaded {len(locations)} locations for TomTom ETA calculations")
            
    except Exception as e:
        print(f"   ⚠️  Error loading locations: {e}")
        # Fallback locations for key dairies
        locations = {
            'depot': {"lat": 33.4484, "lon": -112.0740},
            't&k': {"lat": 33.2855, "lon": -112.1234},  # Example coordinates
            'milky way dairy': {"lat": 33.3456, "lon": -112.2345}  # Example coordinates
        }
    
    return locations

def find_dairy_coordinates(dairy_name, locations):
    """Find coordinates for a dairy by matching name variations"""
    if not dairy_name:
        return None
    
    dairy_lower = dairy_name.lower()
    
    # Direct match
    if dairy_lower in locations:
        return locations[dairy_lower]
    
    # Partial matches for common patterns
    for location_name, coords in locations.items():
        if any(keyword in location_name for keyword in ['t&k', 'milky', 'triple', 'dickman', 'belmont', 'piazzo']):
            if any(keyword in dairy_lower for keyword in ['t&k', 'milky', 'triple', 'dickman', 'belmont', 'piazzo']):
                return coords
    
    return None

def get_vehicle_location_by_id(vehicle_id):
    """Get current GPS location of a truck using Samsara vehicle ID (more direct)"""
    if not vehicle_id:
        return None
    
    try:
        headers = {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}
        
        # Direct vehicle stats call using vehicle ID
        stats_url = "https://api.samsara.com/fleet/vehicles/stats"
        params = {"vehicleIds": [vehicle_id], "types": "gps"}
        
        stats_response = requests.get(stats_url, headers=headers, params=params)
        stats_response.raise_for_status()
        
        stats_data = stats_response.json().get('data', [])
        if not stats_data:
            print(f"   ⚠️  No stats data for vehicle ID {vehicle_id}")
            return None
        
        data = stats_data[0]
        if 'gps' in data and 'latitude' in data['gps']:
            location = {"lat": data['gps']['latitude'], "lon": data['gps']['longitude']}
            print(f"   📍 Found vehicle {vehicle_id} at: {location['lat']:.4f}, {location['lon']:.4f}")
            return location
        else:
            print(f"   ⚠️  No GPS data for vehicle ID {vehicle_id}")
            return None
        
    except Exception as e:
        print(f"   ⚠️  Error getting vehicle location by ID {vehicle_id}: {e}")
        return None

def get_vehicle_location(truck_number):
    """Get current GPS location of a truck from Samsara API"""
    if not truck_number or truck_number == 'TBD':
        return None
    
    try:
        # Get all vehicles first
        vehicles_url = "https://api.samsara.com/fleet/vehicles"
        headers = {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}
        
        response = requests.get(vehicles_url, headers=headers)
        response.raise_for_status()
        all_vehicles = response.json().get('data', [])
        
        # Try to find vehicle with various name formats
        possible_names = [f"DMT {truck_number}", f"TRUCK {truck_number}", truck_number, f"Truck {truck_number}"]
        vehicle_data = None
        
        for target_name in possible_names:
            for vehicle in all_vehicles:
                if vehicle.get('name') == target_name:
                    vehicle_data = vehicle
                    break
            if vehicle_data:
                break
        
        if not vehicle_data:
            print(f"   ⚠️  Could not find truck '{truck_number}' in Samsara")
            return None
        
        # Get vehicle location
        vehicle_id = vehicle_data['id']
        stats_url = "https://api.samsara.com/fleet/vehicles/stats"
        params = {"vehicleIds": [vehicle_id], "types": "gps"}
        
        stats_response = requests.get(stats_url, headers=headers, params=params)
        stats_response.raise_for_status()
        
        stats_data = stats_response.json().get('data', [])
        if not stats_data:
            return None
        
        data = stats_data[0]
        if 'gps' in data and 'latitude' in data['gps']:
            location = {"lat": data['gps']['latitude'], "lon": data['gps']['longitude']}
            print(f"   📍 Found truck {truck_number} at: {location['lat']:.4f}, {location['lon']:.4f}")
            return location
        
        return None
        
    except Exception as e:
        print(f"   ⚠️  Error getting truck location for {truck_number}: {e}")
        return None

if __name__ == "__main__":
    populate_routes_data() 