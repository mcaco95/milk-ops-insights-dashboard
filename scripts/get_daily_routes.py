import requests
import os
import argparse
import pandas as pd
from datetime import date, datetime, timedelta
import json
import math
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import text

# --- Configuration ---
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
SAMSARA_API_TOKEN = os.getenv("SAMSARA_API_TOKEN", "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE") # Use fallback for now
TOMTOM_API_KEY = "s4SRO0ZMWIrxsaAsUrIRLN4R5MZHabTt"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"
HAULER_NUMBER = "77"
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@postgres:5432/dairy_operations")

# --- Definitive Location Mapping ---
# Maps (dairy_name, tank) to the corresponding Samsara address name
DAIRY_LOCATION_MAP = {
    ("Milky Way Dairy (633)", "1"): "Milky Way (633)-Barn 1 (North Barn)",
    ("Milky Way Dairy (633)", "2"): "Milky Way (633) - Barn 2 (South Barn)",
    ("Milky Way Dairy (633)", "3"): "Milky Way (633)-Barn 1 (North Barn)",  # Fallback to Barn 1
    ("Milky Way Dairy (633)", "4"): "Milky Way (633)-Barn 1 (North Barn)",  # Fallback to Barn 1
    ("Milky Way Dairy (633)", "5"): "Milky Way (633)-Barn 1 (North Barn)",  # Fallback to Barn 1
    ("Milky Way Dairy (633)", "6"): "Milky Way (633)-Barn 1 (North Barn)",  # Fallback to Barn 1
    ("Triple G Dairy", "1"): "Triple G (494) - Barn 1 (Main Barn)",
    ("Triple G Dairy", "2"): "Triple G (494) - Barn 1 (Main Barn)",
    ("Triple G Dairy", "3"): "Triple G (494) - Barn 1 (Main Barn)",
    ("Belmont Dairy(701)", "1"): "Belmont (701)",
    ("T&K", "1"): "T&K (348) - Barn 2",  # Use working location
    ("T&K", "2"): "T&K (348) - Barn 2",
    ("T&K", "3"): "T&K (348) - Barn 3",
    ("T&K", "4"): "T&K (348) - Barn 2",  # Use working location
    ("T&K", "5"): "T&K (348) - Barn 2",  # Use working location
    ("T&K", "6"): "T&K (348) - Barn 2",  # Use working location
    ("T&K", "7"): "T&K (348) - Barn 2",  # Use working location
    ("T&K", "8"): "T&K (348) - Barn 2",  # Use working location
    ("T&K", "9"): "T&K (348) - Barn 2",  # Use working location
    ("Arizona Dairy", "1"): "AZ Dairy (395)",
    ("Arizona Dairy", "2"): "AZ Dairy (395)",
    ("Dickman and Sons Dairy (815)", "1"): "Dickman (815)",
    ("Dickman and Sons Dairy (815)", "2"): "Dickman (815)",
    ("Dickman and Sons Dairy (815)", "3"): "Dickman (815)",
    ("D&I Dairy (805)", "1"): "D&I Dairy (805)",
    ("Legendairy LLC", "1"): "Legendairy LLC",
    ("Legendairy LLC", "2"): "Legendairy LLC",
    ("D&I Holsteins (716)", "1"): "D & I Holsteins (716)",
    ("D&I Holsteins (716)", "2"): "D & I Holsteins (716)",
    ("Piazzo Dairy (800)", "1"): "Piazzo Dairy (800)",
    ("Piazzo Dairy (800)", "2"): "Piazzo Dairy (800)",
}

# Hardcoded producer ID mapping extracted from load-summary data
PRODUCER_ID_MAPPING = {
    "60cce07b8ada14e90f0783d9": "T&K",  # 110 records
    "60cce07b8ada14e90f0783b6": "Milky Way Dairy (633)",  # 73 records
    "60cce07b8ada14e90f0783d6": "Triple G Dairy",  # 33 records
    "60cce07b8ada14e90f0783b8": "Dickman and Sons Dairy (815)",  # 27 records
    "60cce07b8ada14e90f0783b7": "Arizona Dairy",  # 24 records
    "60cce07b8ada14e90f0783b1": "Piazzo Dairy (800)",  # 24 records
    "60cce07b8ada14e90f0783b2": "D&I Holsteins (716)",  # 15 records
    "60cce07b8ada14e90f0783b0": "D&I Dairy (805)",  # 9 records
    "676ec1dd1b2d881722b505f3": "Legendairy LLC",  # 8 records
    "60cce07b8ada14e90f0783bf": "Belmont Dairy(701)",  # 2 records
}

# --- Database Functions ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        return psycopg2.connect(DB_URL)
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def get_dairy_id_map(conn):
    """Fetches a map of potential dairy names to the canonical dairy_id."""
    dairy_map = {}
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, milk_movement_names, samsara_location_names FROM dairies")
        for row in cur.fetchall():
            dairy_id, name, milk_names, samsara_names = row
            all_names = [name] + (milk_names or []) + (samsara_names or [])
            for n in all_names:
                if n:
                    normalized = n.lower().replace(' ', '').replace('[', '').replace(']', '').replace('&', '').replace('(', '').replace(')', '').replace('dairy', '')
                    if normalized not in dairy_map:
                         dairy_map[normalized] = dairy_id
    return dairy_map

def is_name_match(script_name, db_names_to_id_map):
    """Finds the matching dairy_id for a name from the script."""
    normalized_script_name = script_name.lower().replace(' ', '').replace('[', '').replace(']', '').replace('&', '').replace('(', '').replace(')', '').replace('dairy', '')
    if normalized_script_name in db_names_to_id_map:
        return db_names_to_id_map[normalized_script_name]
    for db_norm, dairy_id in db_names_to_id_map.items():
        if normalized_script_name in db_norm or db_norm in normalized_script_name:
            return dairy_id
    return None

def upsert_routes_data(conn, routes_data):
    """Inserts or updates route data in the routes_data table."""
    if not routes_data:
        print("No route data to upsert.")
        return 0
    
    data_to_upsert = [
        (d['dairy_id'], d['report_date'], d.get('samsara_route_id'), d['driver_name'], d['truck_id'], d['status'], d.get('estimated_arrival'), d['target_location'])
        for d in routes_data
    ]
    
    query = """
    INSERT INTO routes_data (dairy_id, report_date, samsara_route_id, driver_name, truck_id, status, estimated_arrival, target_location)
    VALUES %s
    ON CONFLICT (dairy_id, report_date, samsara_route_id, driver_name, truck_id)
    DO UPDATE SET
        status = EXCLUDED.status,
        estimated_arrival = EXCLUDED.estimated_arrival,
        last_updated = NOW() AT TIME ZONE 'UTC';
    """
    
    with conn.cursor() as cur:
        execute_values(cur, query, data_to_upsert, template=None, page_size=100)
        conn.commit()
        return cur.rowcount

# --- Helper Functions ---
def get_auth_headers(api_name="mm"):
    """Returns the authorization headers for the API request."""
    if api_name == "samsara":
        return {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}
    return {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}

def get_all_samsara_vehicles():
    """Fetches and prints all vehicle names from Samsara for diagnostics."""
    print("--- Fetching all available vehicle names from Samsara ---")
    all_vehicles = []
    url = "https://api.samsara.com/fleet/vehicles"
    try:
        response = requests.get(url, headers=get_auth_headers("samsara"))
        response.raise_for_status()
        vehicles = response.json().get('data', [])
        for v in vehicles:
            all_vehicles.append(v.get('name', 'N/A'))
        print(f"Samsara knows about the following {len(all_vehicles)} trucks:")
        print(", ".join(sorted(all_vehicles)))
        print("---------------------------------------------------------")
    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not get vehicles from Samsara: {e}")
    # This function is for diagnostics, so we don't return anything.

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

def get_all_samsara_locations():
    """
    Fetches all addresses from the database instead of Samsara API
    Returns them as a dictionary mapping location names to their coordinates.
    """
    print("Loading locations from database...")
    locations = {}
    
    try:
        # Get database connection using existing pattern
        conn = get_db_connection()
        if not conn:
            print("ERROR: Could not connect to database")
            return {}
        
        with conn.cursor() as cur:
            # Query the pre-populated samsara_addresses table
            query = "SELECT name, latitude, longitude FROM samsara_addresses WHERE latitude IS NOT NULL AND longitude IS NOT NULL"
            cur.execute(query)
            addresses = cur.fetchall()
            
            # Convert to the expected format
            for addr in addresses:
                name, latitude, longitude = addr
                if name and name.strip():  # Skip empty names
                    locations[name] = {
                        "lat": float(latitude), 
                        "lon": float(longitude)
                    }
        
        conn.close()
        print(f"Successfully loaded {len(locations)} locations from database.")
        return locations
        
    except Exception as e:
        print(f"ERROR: Could not get locations from database: {e}")
        print("Falling back to empty locations dict...")
        return {}

def get_vehicle_location_and_speed(truck_number):
    """
    Disabled vehicle location API calls to avoid scheduler issues.
    Returns None for both location and speed.
    """
    print(f"    - Vehicle location API disabled for truck {truck_number}")
    # Get all vehicles first
    try:
        vehicles_url = "https://api.samsara.com/fleet/vehicles"
        response = requests.get(vehicles_url, headers=get_auth_headers("samsara"))
        response.raise_for_status()
        all_vehicles = response.json().get('data', [])
        
        # Try exact name matches
        possible_names = [f"DMT {truck_number}", f"TRUCK {truck_number}", truck_number]
        vehicle_data = None
        
        for target_name in possible_names:
            print(f"    - Looking for vehicle with exact name: '{target_name}'")
            for vehicle in all_vehicles:
                if vehicle.get('name') == target_name:
                    vehicle_data = vehicle
                    print(f"    - SUCCESS: Found exact match - ID {vehicle_data['id']}, Name: {vehicle_data['name']}")
                    break
            if vehicle_data:
                break
        
        if not vehicle_data:
            print(f"    - FAILED: Could not find vehicle '{truck_number}' with any name format.")
            print(f"    - Available vehicle names: {[v.get('name') for v in all_vehicles[:10]]}...")
            return None, None
            
    except requests.exceptions.RequestException as e:
        print(f"    - Exception getting vehicles: {e}")
        return None, None
    
    # Now get the location and speed data
    try:
        vehicle_id = vehicle_data['id']
        stats_url = "https://api.samsara.com/fleet/vehicles/stats"
        params = {
            "vehicleIds": [vehicle_id],
            "types": "gps,ecuSpeedMph"
        }
        print(f"    - Making API call to: {stats_url} with params: {params}")
        stats_response = requests.get(stats_url, headers=get_auth_headers("samsara"), params=params)
        stats_response.raise_for_status()
        
        stats_data = stats_response.json().get('data', [])
        print(f"    - DEBUG: Raw stats data received from Samsara: {stats_data}")
        if not stats_data:
            print("    - No stats data returned from Samsara API")
            return None, None
            
        data = stats_data[0] 
        location = None
        speed_mph = None
        
        if 'gps' in data and 'latitude' in data['gps']:
            location = {"lat": data['gps']['latitude'], "lon": data['gps']['longitude']}
            print(f"    - GPS data found: {location}")
        else:
            print(f"    - No GPS data in response. Available keys: {list(data.keys())}")
            
        if 'ecuSpeedMph' in data and 'value' in data['ecuSpeedMph']:
            speed_mph = data['ecuSpeedMph']['value']
            print(f"    - Speed data found: {speed_mph} mph")
        else:
            print(f"    - No speed data in response.")
            
        return location, speed_mph
    except (requests.exceptions.RequestException, KeyError, IndexError) as e:
        print(f"    - Exception during stats API call: {e}")
        return None, None

def get_load_summaries(date_str):
    """Fetches load summary data from Milk Moovement."""
    url = f"{API_BASE_URL}/pickups/load-summary"
    params = {"start_date": date_str, "end_date": date_str}
    try:
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching load summaries: {e}")
        return None

def get_schedules_data(start_date, end_date):
    """Fetches scheduled routes data from Milk Movement for future routes."""
    url = f"{API_BASE_URL}/schedules"
    params = {"start_date": start_date, "end_date": end_date}
    try:
        print(f"Fetching schedules from {start_date} to {end_date}...")
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        
        schedules = response.json()
        print(f"Found {len(schedules)} total schedules")
        
        # Filter to hauler 77 only and convert to pickup-like format
        hauler_77_schedules = []
        for schedule in schedules:
            hauler_info = schedule.get('hauler', {})
            if str(hauler_info.get('hauler_number', '')) == HAULER_NUMBER:
                hauler_77_schedules.append(schedule)
        
        print(f"Found {len(hauler_77_schedules)} schedules for hauler {HAULER_NUMBER}")
        return hauler_77_schedules
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching schedules: {e}")
        return []

def get_producer_details(producer_ids):
    """Get producer details using hardcoded mapping from load-summary data"""
    if not producer_ids:
        return {}
    
    producer_map = {}
    for producer_id in producer_ids:
        if producer_id in PRODUCER_ID_MAPPING:
            producer_map[producer_id] = {
                'name': PRODUCER_ID_MAPPING[producer_id],
                'tank': '1'  # Default tank - actual tank info comes from route logic
            }
        else:
            print(f"Warning: Unknown producer ID {producer_id} not in mapping")
    
    return producer_map

def convert_schedule_to_pickup_format(schedule):
    """Convert a schedule record to pickup format for consistent processing."""
    # Extract basic info
    start_date = schedule.get('start_date', '')
    route_name = schedule.get('route_name', 'N/A')
    lt_number = schedule.get('lt_number', 'N/A')
    amount = schedule.get('amount', 0)
    
    # Extract hauler info
    hauler_info = schedule.get('hauler', {})
    hauler_name = hauler_info.get('name', 'Unknown')
    
    # Extract processor info
    processor_info = schedule.get('destination_processor', {})
    processor_name = processor_info.get('name', 'Unknown')
    
    # IMPROVED: Better handling of producer IDs
    origin_producer_ids = schedule.get('origin_producer_ids', [])
    
    # Filter out empty/null producer IDs
    valid_producer_ids = [pid for pid in origin_producer_ids if pid and pid.strip()]
    
    if valid_producer_ids:
        # Get producer details for these IDs
        producer_details = get_producer_details(valid_producer_ids)
        
        if producer_details:
            # Use the first producer as the primary (most routes have 1-2 producers)
            first_producer_id = valid_producer_ids[0]
            if first_producer_id in producer_details:
                producer_name = producer_details[first_producer_id]['name']
                producer_tank = producer_details[first_producer_id]['tank']
            else:
                # Fallback for unknown producer IDs
                if len(valid_producer_ids) > 1:
                    producer_name = "Multiple Dairies"
                    producer_tank = "Multiple" 
                else:
                    producer_name = f"Unknown Dairy ({first_producer_id[:8]}...)"
                    producer_tank = "Unknown"
        else:
            # No producer details found
            if len(valid_producer_ids) > 1:
                producer_name = "Multiple Dairies"
                producer_tank = "Multiple"
            else:
                producer_name = f"Unknown Dairy ({valid_producer_ids[0][:8]}...)"
                producer_tank = "Unknown"
    else:
        # No valid producer IDs at all
        # Try to infer from route name or other fields
        if route_name and route_name != 'N/A':
            producer_name = f"Route {route_name}"
            producer_tank = "TBD"
        else:
            producer_name = "Unassigned Route" 
            producer_tank = "TBD"
    
    # Create pickup-like record
    pickup_record = {
        'pickup_date': start_date,
        'route_number': route_name,
        'invoice_number': lt_number,
        'pickup_amount': amount,
        'producer_name': producer_name,
        'producer_tank': producer_tank,
        'processor_name': processor_name,
        'hauler_name': hauler_name,
        'hauler_number': HAULER_NUMBER,
        'truck_number': 'TBD',  # Schedules may not have truck assigned yet
        'driver': 'TBD',  # Schedules may not have driver assigned yet
        'dropoff_date': None,  # Future routes haven't been delivered
        'geofence_enter_time': None,  # Future routes haven't started
        'schedule_status': 'scheduled'  # Mark this as scheduled data
    }
    
    return pickup_record

def get_combined_routes_data(target_date):
    """Get combined data from both pickups and schedules APIs."""
    print("=== FETCHING COMBINED ROUTES DATA ===")
    
    # Get pickups for today (active/completed routes)
    print("1. Fetching pickups (active/completed routes)...")
    pickups = get_load_summaries(target_date)
    pickup_records = pickups if pickups else []
    
    # Get schedules for today + tomorrow (future routes)  
    target_date_obj = datetime.strptime(target_date, "%Y-%m-%d")
    end_date = (target_date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
    
    print("2. Fetching schedules (future routes)...")
    schedules = get_schedules_data(target_date, end_date)
    
    # Convert schedules to pickup format
    schedule_records = []
    for schedule in schedules:
        try:
            pickup_record = convert_schedule_to_pickup_format(schedule)
            schedule_records.append(pickup_record)
        except Exception as e:
            print(f"Warning: Could not convert schedule record: {e}")
            continue
    
    # Combine both datasets
    all_records = pickup_records + schedule_records
    
    print(f"Combined: {len(pickup_records)} pickups + {len(schedule_records)} schedules = {len(all_records)} total records")
    return all_records

def generate_routes_report(summaries, samsara_locations, target_dairy=None):
    """Transforms data into a dairy-centric routes report using geofence status and TomTom ETA."""
    if not summaries:
        return pd.DataFrame()

    df = pd.DataFrame(summaries)
    df = df[df["hauler_number"] == HAULER_NUMBER].copy()
    if target_dairy:
        df = df[df["producer_name"] == target_dairy].copy()

    if df.empty:
        return pd.DataFrame()

    report_data = []
    
    for _, row in df.iterrows():
        status = 'Unknown'
        eta = 'N/A'
        speed = 'N/A'

        # More detailed logging
        print(f"\nProcessing LT#: {row['invoice_number']} for '{row['producer_name']}' (Tank: {row['producer_tank']}, Truck: {row['truck_number']})")

        # NEW: Check if this route has Samsara enhancement
        if row.get('samsara_enhanced', False):
            status = row['samsara_status']
            print(f"  - Using Samsara real-time status: '{status}'")
        else:
            # EXISTING: Check if this is scheduled data first
            if row.get('schedule_status') == 'scheduled':
                status = 'Scheduled'
                pickup_date = pd.to_datetime(row['pickup_date'])
                current_time = datetime.now()
                
                # Make sure both datetimes are comparable (remove timezone info if present)
                if pickup_date.tz is not None:
                    pickup_date = pickup_date.tz_localize(None)
                
                # Calculate time until scheduled pickup
                if pickup_date > current_time:
                    hours_until = (pickup_date - current_time).total_seconds() / 3600
                    if hours_until > 24:
                        eta = f"In {int(hours_until/24)} days"
                    else:
                        eta = f"In {int(hours_until)}h"
                else:
                    eta = "Scheduled"
                
                print(f"  - Schedule Status: 'Scheduled' (ETA: {eta})")
            else:
                # EXISTING: Determine Status from Geofence data for active/completed pickups
                if pd.notna(row['dropoff_date']):
                    status = 'Completed'
                elif pd.notna(row['geofence_enter_time']):
                    status = 'Arrived'
                else:
                    status = 'En Route'
                
                print(f"  - Geofence Status: '{status}'")

        # Enhanced ETA calculation
        if status == 'En Route':
            print("  - Status is 'En Route'. Attempting to calculate live ETA...")
            vehicle_loc, speed_mph = get_vehicle_location_and_speed(row['truck_number'])
            
            # --- Improved Location Lookup ---
            # First, try to find an exact match for (producer, tank)
            samsara_location_name = DAIRY_LOCATION_MAP.get((row['producer_name'], row['producer_tank']))
            if not samsara_location_name:
                print(f"    - No specific mapping for '{row['producer_name']}' Tank '{row['producer_tank']}'. Looking for a general location...")
                # If no exact match, try to find a match for just the producer name with any tank
                for (p_name, _), loc_name in DAIRY_LOCATION_MAP.items():
                    if p_name == row['producer_name']:
                        samsara_location_name = loc_name
                        print(f"    - Found general location for '{row['producer_name']}': {samsara_location_name}")
                        break
            # --- End Improved Lookup ---
            
            dairy_loc = samsara_locations.get(samsara_location_name)
            
            print(f"    - Truck Location Found: {'Yes' if vehicle_loc else 'No'}")
            print(f"    - Dairy Location Found: {'Yes' if dairy_loc else 'No'} (Samsara Name: '{samsara_location_name}')")

            if speed_mph is not None:
                speed = f"{int(speed_mph)} mph"

            # Store route information
            if vehicle_loc and dairy_loc:
                print("    - Both locations found. Calling TomTom API for traffic-aware ETA...")
                eta_minutes = get_live_eta(vehicle_loc, dairy_loc)
                if eta_minutes is not None:
                    eta = f"Approx. {int(eta_minutes)} mins"
                    print(f"    - TomTom ETA Received: {eta}")
                else:
                    eta = "ETA Error"
                    print("    - TomTom API call failed.")
            else:
                eta = "Location Error"
                print("    - Cannot calculate ETA, missing one or more locations.")
        else:
            print("  - Skipping ETA calculation (Status is not 'En Route').")

        # Get route information from the data
        route_info = row.get('route_number', row.get('route_name', row.get('invoice_number', 'N/A')))
        
        # Enhanced start time parsing - use Samsara data if available
        start_time = 'N/A'
        try:
            # NEW: Prefer Samsara route start time if available
            if row.get('samsara_enhanced', False) and row.get('route_start_time'):
                samsara_start_time = row['route_start_time']
                if isinstance(samsara_start_time, str):
                    # Parse Samsara ISO format: "2025-06-03T15:08:19.007Z"
                    dt = pd.to_datetime(samsara_start_time)
                    start_time = dt.strftime('%H:%M')
                    print(f"    - Using Samsara start time: {start_time}")
                else:
                    raise ValueError("Invalid Samsara start time format")
            else:
                # EXISTING: Use MM pickup_date
                pickup_date_raw = row['pickup_date']
                if pickup_date_raw:
                    # Try to parse the date - handle both formats
                    if isinstance(pickup_date_raw, str):
                        # Handle ISO format: "2025-06-09T07:00:00Z" or "2025-06-09T07:00:00"
                        if 'T' in pickup_date_raw:
                            date_part, time_part = pickup_date_raw.split('T')
                            time_only = time_part.split('Z')[0].split('.')[0]  # Remove timezone and microseconds
                            hour_min = time_only[:5]  # Get HH:MM
                            start_time = hour_min
                        else:
                            # Try direct parsing
                            parsed_date = pd.to_datetime(pickup_date_raw)
                            start_time = parsed_date.strftime('%H:%M')
                    else:
                        # Already a datetime object
                        parsed_date = pd.to_datetime(pickup_date_raw)
                        start_time = parsed_date.strftime('%H:%M')
        except Exception as e:
            print(f"    - Warning: Could not parse start time '{row.get('pickup_date', 'N/A')}': {e}")
            start_time = 'N/A'
        
        report_data.append({
            'Start Time': start_time,
            'Route': route_info,
            'Dairy': row['producer_name'],
            'Tank': row['producer_tank'],
            'Processor': row['processor_name'] or 'TBD',
            'Status': status,
            'ETA': eta,
            'Speed': speed,
            'Truck #': row['truck_number'],
            'Driver': row['driver']
        })

    report_df = pd.DataFrame(report_data)
    return report_df.sort_values(by='Start Time').reset_index(drop=True)

def process_routes_data(df, dairy_id_map):
    """Processes the DataFrame from the API into a structured list for the database."""
    processed = []
    today = datetime.now().date()
    
    for _, row in df.iterrows():
        dairy_name = row['Dairy']
        
        # IMPROVED: Skip routes that don't have real dairy assignments
        if dairy_name in ['Unassigned Route', 'Multiple Dairies'] or dairy_name.startswith('Route ') or dairy_name.startswith('Unknown Dairy ('):
            print(f"Skipping unassigned/unknown route: {dairy_name} (LT: {row.get('Route', 'N/A')})")
            continue
            
        dairy_id = is_name_match(dairy_name, dairy_id_map)
        
        if not dairy_id:
            print(f"Warning: Could not match route dairy '{dairy_name}' to any known dairy. Skipping.")
            continue
        
        # Enhanced status mapping - includes new DairyMen 4-status system
        status_mapping = {
            'Completed': 'completed',
            'Filling Tank': 'active',  # NEW: At dairy loading milk
            'At Dairy': 'active',     # Legacy compatibility 
            'En Route': 'active',     # Traveling to dairy
            'Scheduled': 'scheduled'
        }
        
        db_status = status_mapping.get(row['Status'], 'scheduled')
        
        # For scheduled routes, use the scheduled date instead of today
        if row['Status'] == 'Scheduled':
            try:
                pickup_date = pd.to_datetime(row['Start Time'], format='%H:%M')
                # This is just time, we need to figure out the actual date
                # For now, assume it's either today or tomorrow based on time
                current_hour = datetime.now().hour
                if pickup_date.hour < current_hour:
                    # Likely tomorrow
                    report_date = today + timedelta(days=1)
                else:
                    # Likely today
                    report_date = today
            except:
                # Default to today if we can't parse
                report_date = today
        else:
            report_date = today
        
        # Enhanced ETA handling - preserve Samsara real-time ETAs
        eta_value = row['ETA']
        estimated_arrival = None
        
        # Only try to parse if it looks like an actual time/date
        if eta_value and eta_value not in ['N/A', 'TBD', 'Location Error', 'ETA Error', 'Scheduled'] and not eta_value.startswith('In ') and not eta_value.startswith('Approx.'):
            try:
                estimated_arrival = pd.to_datetime(eta_value).isoformat()
            except:
                estimated_arrival = None
        
        processed.append({
            'dairy_id': dairy_id,
            'report_date': report_date,
            'samsara_route_id': row['Route'],
            'driver_name': row['Driver'],
            'truck_id': row['Truck #'],
            'status': db_status,
            'estimated_arrival': estimated_arrival,
            'target_location': row['Dairy'],
        })
    return processed

# --- Samsara Routes API Integration ---
def extract_lt_number_from_route_name(route_name):
    """Extract LT/invoice number from Samsara route name."""
    # Pattern: "Route 75: CTD93137 Dickman (815)-Safeway-Tank 1"
    # Look for alphanumeric code after route number and colon
    import re
    match = re.search(r'Route\s+\d+:\s+([A-Z]{3}\d{5})', route_name)
    if match:
        return match.group(1)
    return None

def find_dairy_stop(stops):
    """Find the dairy stop in Samsara route (middle stop, not processor)."""
    if len(stops) < 2:
        return None
    
    # Usually the dairy is the second stop (after start location, before processor)
    for i, stop in enumerate(stops):
        # Skip first and last stops (usually processors/depots)
        if i > 0 and i < len(stops) - 1:
            return stop
    
    # Fallback: look for stops that aren't common processors
    processors = ['UDA', 'Safeway', 'Shamrock', 'Kroger', 'Fairlife', 'Schreiber']
    for stop in stops:
        stop_name = stop.get('name', '')
        if not any(proc in stop_name for proc in processors):
            return stop
    
    return None

def get_samsara_routes_data(days_back=7):
    """
    Fetches routes from Samsara API for the past N days.
    Returns a dictionary mapping LT numbers to route status data.
    """
    print("Fetching real-time route data from Samsara...")
    
    from datetime import datetime, timedelta, timezone
    
    url = "https://api.samsara.com/fleet/routes"
    
    # Get routes from past week
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=days_back)
    params = {
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "limit": 100  # Get more routes for matching
    }
    
    samsara_routes_map = {}
    
    try:
        response = requests.get(url, headers=get_auth_headers("samsara"), params=params)
        response.raise_for_status()
        routes = response.json().get('data', [])
        
        print(f"Found {len(routes)} Samsara routes to analyze...")
        
        for route in routes:
            route_name = route.get('name', '')
            stops = route.get('stops', [])
            
            # Extract LT number
            lt_number = extract_lt_number_from_route_name(route_name)
            if not lt_number:
                continue  # Skip routes without LT numbers
            
            # Find dairy stop
            dairy_stop = find_dairy_stop(stops)
            if not dairy_stop:
                continue  # Skip routes without dairy stops
            
            # Determine real-time status based on dairy stop
            dairy_state = dairy_stop.get('state', 'unknown')
            dairy_name = dairy_stop.get('name', 'Unknown')
            
            # FIXED: Get the actual departure time from depot (first stop)
            actual_route_start = None
            scheduled_route_start = route.get('scheduledRouteStartTime')
            
            # Try to get actual departure time from first stop
            if stops:
                first_stop = stops[0]
                actual_departure_from_depot = first_stop.get('actualDepartureTime')
                if actual_departure_from_depot:
                    actual_route_start = actual_departure_from_depot
                    print(f"    LT#{lt_number}: Using first stop departure: {actual_route_start}")
                else:
                    # Fallback: use scheduled departure from first stop
                    scheduled_departure_from_depot = first_stop.get('scheduledDepartureTime')
                    if scheduled_departure_from_depot:
                        actual_route_start = scheduled_departure_from_depot
                        print(f"    LT#{lt_number}: Using first stop scheduled departure: {actual_route_start}")
                    else:
                        # Last resort: use route level times
                        actual_route_start = route.get('actualRouteStartTime') or scheduled_route_start
                        print(f"    LT#{lt_number}: Using route-level start time: {actual_route_start}")
            
            # Get dairy timing information
            dairy_arrival = dairy_stop.get('actualArrivalTime')
            dairy_departure = dairy_stop.get('actualDepartureTime')
            
            # Map Samsara states to our status system
            if dairy_state == 'departed':
                samsara_status = 'Completed'
                status_updated_time = dairy_departure
            elif dairy_state == 'arrived':
                samsara_status = 'At Dairy' 
                status_updated_time = dairy_arrival
            elif dairy_state in ['enRoute', 'dispatched']:
                samsara_status = 'En Route'
                status_updated_time = actual_route_start or scheduled_route_start
            else:
                samsara_status = 'Scheduled'
                status_updated_time = scheduled_route_start
            
            samsara_routes_map[lt_number] = {
                'samsara_route_id': route.get('id'),
                'route_name': route_name,
                'dairy_name': dairy_name,
                'samsara_status': samsara_status,
                'dairy_state': dairy_state,
                'route_start_time': actual_route_start or scheduled_route_start,  # NOW: Departure from depot
                'dairy_arrival_time': dairy_arrival,
                'dairy_departure_time': dairy_departure,
                'status_updated_time': status_updated_time,
                'driver_name': route.get('driver', {}).get('name', 'Unknown')
            }
            
        print(f"Successfully mapped {len(samsara_routes_map)} routes with LT numbers")
        return samsara_routes_map
        
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch Samsara routes: {e}")
        return {}

def enhance_mm_data_with_samsara(mm_summaries, samsara_routes_map):
    """
    Enhances Milk Movement data with real-time Samsara status information.
    Matches by LT/invoice numbers and updates status accordingly.
    """
    if not samsara_routes_map:
        print("No Samsara data available for enhancement")
        return mm_summaries
    
    enhanced_summaries = []
    matched_count = 0
    
    for summary in mm_summaries:
        # Try to match by invoice number (LT number)
        lt_number = summary.get('invoice_number', '').strip()
        
        if lt_number and lt_number in samsara_routes_map:
            # Found a match! Enhance with Samsara data
            samsara_data = samsara_routes_map[lt_number]
            
            print(f"✅ Matched LT#{lt_number}: MM='{summary.get('producer_name')}' ↔ Samsara='{samsara_data['dairy_name']}' (Status: {samsara_data['samsara_status']})")
            
            # Create enhanced summary with Samsara real-time data
            enhanced_summary = summary.copy()
            
            # Override status with Samsara real-time status
            enhanced_summary['samsara_enhanced'] = True
            enhanced_summary['samsara_status'] = samsara_data['samsara_status']
            enhanced_summary['samsara_route_id'] = samsara_data['samsara_route_id']
            enhanced_summary['samsara_dairy_name'] = samsara_data['dairy_name']
            enhanced_summary['route_start_time'] = samsara_data['route_start_time']
            enhanced_summary['dairy_arrival_time'] = samsara_data['dairy_arrival_time']
            enhanced_summary['dairy_departure_time'] = samsara_data['dairy_departure_time']
            
            # Use Samsara driver name if available and different
            if samsara_data['driver_name'] != 'Unknown' and samsara_data['driver_name'] != summary.get('driver', ''):
                enhanced_summary['driver'] = samsara_data['driver_name']
            
            enhanced_summaries.append(enhanced_summary)
            matched_count += 1
        else:
            # No match found, keep original MM data
            enhanced_summaries.append(summary)
    
    print(f"Enhanced {matched_count}/{len(mm_summaries)} routes with Samsara real-time data")
    return enhanced_summaries

def main():
    """Main function to fetch, process, and store daily routes data."""
    print("--- Starting Enhanced Route Data Ingestion (MM + Samsara) ---")
    
    conn = get_db_connection()
    if not conn:
        return
        
    try:
        # Step 1: Fetch Samsara Routes data for real-time enhancement
        print("\n🔄 Step 1: Fetching Samsara routes for real-time status...")
        samsara_routes_map = get_samsara_routes_data(days_back=7)
        
        # Step 2: Get combined data from Milk Movement APIs
        try:
            print("\n🔄 Step 2: Using combined approach (MM pickups + schedules)...")
            combined_data = get_combined_routes_data(date.today().strftime("%Y-%m-%d"))
            if combined_data:
                print(f"✅ MM data successful: {len(combined_data)} routes")
            else:
                print("⚠️ Combined approach returned no data, falling back to old method...")
                raise Exception("No combined data")
                
        except Exception as e:
            print(f"❌ Combined approach failed: {e}")
            print("🔄 Falling back to MM pickups only...")
            
            # FALLBACK: Use original method
            summaries = get_load_summaries(date.today().strftime("%Y-%m-%d"))
            if summaries is None:
                return
            combined_data = summaries
        
        # Step 3: Enhance MM data with Samsara real-time status
        print(f"\n🔄 Step 3: Enhancing {len(combined_data)} MM routes with Samsara data...")
        enhanced_data = enhance_mm_data_with_samsara(combined_data, samsara_routes_map)
        
        # Step 4: Generate routes report with enhanced data
        print(f"\n🔄 Step 4: Generating routes report...")
        report = generate_routes_report(enhanced_data, get_all_samsara_locations())
        
        if report.empty:
            print("No routes returned from enhanced processing.")
            return

        # Step 5: Get dairy mapping from DB
        dairy_id_map = get_dairy_id_map(conn)
        if not dairy_id_map:
            print("Error: Could not retrieve dairy mapping. Aborting.")
            return

        # Step 6: Process data
        routes_data = process_routes_data(report, dairy_id_map)
        
        # Step 7: Upsert data
        print(f"\n🔄 Step 7: Upserting {len(routes_data)} enhanced route records...")
        rows_affected = upsert_routes_data(conn, routes_data)
        
        print(f"\n--- Enhanced Route Data Ingestion Complete ---")
        print(f"✅ {rows_affected} records were inserted or updated in the database.")
        print(f"✅ Enhanced {len([r for r in enhanced_data if r.get('samsara_enhanced')])} routes with real-time Samsara data")

    except Exception as e:
        print(f"❌ Fatal error in main processing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 