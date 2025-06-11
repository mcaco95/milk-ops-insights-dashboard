import requests
import os
import argparse
import pandas as pd
from datetime import date, datetime, timedelta
import json
import math
import pytz
import re

# --- Configuration ---
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
TOMTOM_API_KEY = "s4SRO0ZMWIrxsaAsUrIRLN4R5MZHabTt"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"
HAULER_NUMBER = "77"

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
    Fetches all addresses from the Samsara API and returns them as a dictionary
    mapping location names to their coordinates.
    """
    print("Fetching all locations (dairies, processors) from Samsara...")
    url = "https://api.samsara.com/addresses"
    locations = {}
    try:
        response = requests.get(url, headers=get_auth_headers("samsara"))
        response.raise_for_status()
        addresses = response.json().get('data', [])
        for addr in addresses:
            if 'name' in addr and 'latitude' in addr and 'longitude' in addr:
                locations[addr['name']] = {"lat": addr['latitude'], "lon": addr['longitude']}
        print(f"Successfully loaded {len(locations)} locations.")
        return locations
    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not get locations from Samsara: {e}")
        return {}

def get_vehicle_location_and_speed(truck_number):
    """
    Fetches a vehicle's real-time location and speed from the Samsara API.
    Gets all vehicles and matches by exact name.
    """
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

def generate_routes_report(summaries, samsara_locations, target_dairy=None):
    """
    Transforms data into a dairy-centric routes report using DairyMen business logic.
    Implements 4-status system: Scheduled, En Route, Filling Tank, Completed
    ETA calculation only for 'En Route' status (traveling TO dairy)
    """
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
        status = 'Scheduled'  # Default status
        eta = 'N/A'
        speed = 'N/A'

        # More detailed logging
        print(f"\nProcessing LT#: {row['invoice_number']} for '{row['producer_name']}' (Tank: {row['producer_tank']}, Truck: {row['truck_number']})")

        # Check if this route has Samsara enhancement
        if row.get('samsara_enhanced', False):
            status = row['samsara_status']
            print(f"  - Using Samsara real-time status: '{status}' (DairyMen business logic)")
            
            # Status-specific ETA handling using PROVEN 4-status system
            if status == 'En Route':
                # Only calculate live ETA when traveling TO dairy
                print("  - Status is 'En Route' - calculating live ETA to dairy...")
                vehicle_loc, speed_mph = get_vehicle_location_and_speed(row['truck_number'])
                
                # Get dairy location
                samsara_location_name = DAIRY_LOCATION_MAP.get((row['producer_name'], row['producer_tank']))
                if not samsara_location_name:
                    for (p_name, _), loc_name in DAIRY_LOCATION_MAP.items():
                        if p_name == row['producer_name']:
                            samsara_location_name = loc_name
                            break
                
                dairy_loc = samsara_locations.get(samsara_location_name)
                
                if speed_mph is not None:
                    speed = f"{int(speed_mph)} mph"
                
                if vehicle_loc and dairy_loc:
                    eta_minutes = get_live_eta(vehicle_loc, dairy_loc)
                    if eta_minutes is not None:
                        eta = f"ETA {int(eta_minutes)} mins"
                        print(f"    - Live ETA to dairy: {eta}")
                    else:
                        eta = "ETA Error"
                else:
                    eta = "Location Error"
                    
            elif status == 'Filling Tank':
                # Show arrival time at dairy (when started filling)
                if row.get('dairy_arrival_time'):
                    try:
                        # Parse MST time that's already converted
                        arrival_time_str = row['dairy_arrival_time']
                        if 'T' in arrival_time_str:
                            dt = datetime.fromisoformat(arrival_time_str)
                            eta = f"Arrived {dt.strftime('%H:%M')}"
                            print(f"    - At dairy since: {eta}")
                        else:
                            eta = "At Dairy"
                    except Exception as e:
                        print(f"    - Error parsing arrival time: {e}")
                        eta = "At Dairy"
                else:
                    eta = "At Dairy"
                    
            elif status == 'Completed':
                # Show departure time from dairy (when finished pickup)
                if row.get('dairy_departure_time'):
                    try:
                        # Parse MST time that's already converted
                        departure_time_str = row['dairy_departure_time']
                        if 'T' in departure_time_str:
                            dt = datetime.fromisoformat(departure_time_str)
                            eta = f"Left {dt.strftime('%H:%M')}"
                            print(f"    - Left dairy at: {eta}")
                        else:
                            eta = "Completed"
                    except Exception as e:
                        print(f"    - Error parsing departure time: {e}")
                        eta = "Completed"
                else:
                    eta = "Completed"
                    
            else:  # Scheduled
                eta = "Not Started"
                
        else:
            # Fallback to original geofence logic for non-Samsara routes
            print("  - Using fallback geofence logic (no Samsara data)")
            if pd.notna(row['dropoff_date']):
                status = 'Completed'
                eta = "Completed"
            elif pd.notna(row['geofence_enter_time']):
                status = 'Filling Tank'
                eta = "At Dairy"
            else:
                status = 'En Route'
                
                # Calculate ETA for En Route status
                vehicle_loc, speed_mph = get_vehicle_location_and_speed(row['truck_number'])
                samsara_location_name = DAIRY_LOCATION_MAP.get((row['producer_name'], row['producer_tank']))
                if not samsara_location_name:
                    for (p_name, _), loc_name in DAIRY_LOCATION_MAP.items():
                        if p_name == row['producer_name']:
                            samsara_location_name = loc_name
                            break
                
                dairy_loc = samsara_locations.get(samsara_location_name)
                
                if speed_mph is not None:
                    speed = f"{int(speed_mph)} mph"
                
                if vehicle_loc and dairy_loc:
                    eta_minutes = get_live_eta(vehicle_loc, dairy_loc)
                    if eta_minutes is not None:
                        eta = f"Approx. {int(eta_minutes)} mins"
                    else:
                        eta = "ETA Error"
                else:
                    eta = "Location Error"

        # Get route information
        route_info = row.get('route_number', row.get('route_name', row.get('invoice_number', 'N/A')))
        
        # Enhanced start time parsing - use Samsara data if available (already in MST)
        start_time = 'N/A'
        try:
            if row.get('samsara_enhanced', False) and row.get('route_start_time'):
                # Samsara time already converted to MST
                samsara_start_time = row['route_start_time']
                if isinstance(samsara_start_time, str):
                    dt = pd.to_datetime(samsara_start_time)
                    start_time = dt.strftime('%H:%M')
                    print(f"    - Using Samsara start time (MST): {start_time}")
                else:
                    raise ValueError("Invalid Samsara start time format")
            else:
                # Use MM pickup_date
                pickup_date_raw = row['pickup_date']
                if pickup_date_raw:
                    if isinstance(pickup_date_raw, str):
                        if 'T' in pickup_date_raw:
                            date_part, time_part = pickup_date_raw.split('T')
                            time_only = time_part.split('Z')[0].split('.')[0]
                            hour_min = time_only[:5]
                            start_time = hour_min
                        else:
                            parsed_date = pd.to_datetime(pickup_date_raw)
                            start_time = parsed_date.strftime('%H:%M')
                    else:
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
            'Status': status,  # Now uses 4-status system
            'ETA': eta,
            'Speed': speed,
            'Truck #': row['truck_number'],
            'Driver': row['driver']
        })

    report_df = pd.DataFrame(report_data)
    return report_df.sort_values(by='Start Time').reset_index(drop=True)

def enhance_mm_data_with_samsara(mm_summaries, samsara_routes_map):
    """
    PROVEN WORKING LOGIC from debug_api_merger.py
    Enhances Milk Movement data with real-time Samsara status information.
    """
    if not samsara_routes_map:
        print("No Samsara data available for enhancement")
        return mm_summaries
    
    enhanced_summaries = []
    matched_count = 0
    
    for summary in mm_summaries:
        # Try to match by invoice number (LT number) - SAME AS WORKING SCRIPT
        lt_number = summary.get('invoice_number', '').strip()
        
        if lt_number and lt_number in samsara_routes_map:
            # Found a match! Use PROVEN WORKING LOGIC
            samsara_data = samsara_routes_map[lt_number]
            
            print(f"✅ Matched LT#{lt_number}: MM='{summary.get('producer_name')}' ↔ Samsara='{samsara_data['dairy_name']}' (Status: {samsara_data['samsara_status']})")
            
            # Create enhanced summary with Samsara real-time data
            enhanced_summary = summary.copy()
            
            # Use WORKING STATUS LOGIC from debug script
            enhanced_summary['samsara_enhanced'] = True
            enhanced_summary['samsara_status'] = samsara_data['samsara_status']  # Completed, En Route, etc.
            enhanced_summary['samsara_route_id'] = samsara_data['samsara_route_id']
            enhanced_summary['samsara_dairy_name'] = samsara_data['dairy_name']
            
            # Use WORKING TIME LOGIC from debug script (times already in MST)
            enhanced_summary['route_start_time'] = samsara_data['route_start_time']
            enhanced_summary['dairy_arrival_time'] = samsara_data['dairy_arrival_time']
            enhanced_summary['dairy_departure_time'] = samsara_data['dairy_departure_time']
            enhanced_summary['depot_departure_time'] = samsara_data['depot_departure_time']
            
            # Use Samsara driver name if available
            if samsara_data['driver_name'] != 'Unknown':
                enhanced_summary['driver'] = samsara_data['driver_name']
            
            enhanced_summaries.append(enhanced_summary)
            matched_count += 1
        else:
            # No match found, keep original MM data
            enhanced_summaries.append(summary)
    
    print(f"Enhanced {matched_count}/{len(mm_summaries)} routes with PROVEN Samsara logic")
    return enhanced_summaries

def get_samsara_routes_data(days_back=7, target_date=None):
    """
    PROVEN WORKING LOGIC from debug_api_merger.py
    Fetches routes from Samsara API and returns dictionary mapping LT numbers to route data.
    Uses our PROVEN 4-status system that works perfectly.
    """
    print("Fetching real-time route data from Samsara...")
    
    from datetime import datetime, timedelta, timezone
    import pytz
    
    url = "https://api.samsara.com/fleet/routes"
    
    # Get routes from today only (or specific date)
    if target_date:
        target_dt = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        start_time = target_dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end_time = target_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
        print(f"Getting Samsara routes for specific date: {target_date}")
    else:
        # Get today's data
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        start_time = today
        end_time = tomorrow
        print(f"Getting Samsara routes for today")
    
    params = {
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "limit": 500
    }
    
    headers = {
        "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
        "Accept": "application/json"
    }
    
    # PROVEN MST TIMEZONE LOGIC from debug script
    mst = pytz.timezone('America/Phoenix')
    
    samsara_routes_map = {}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        routes = data.get('data', [])
        
        print(f"Found {len(routes)} Samsara routes to analyze...")
        
        for route in routes:
            # Extract LT number from route name - SAME AS WORKING SCRIPT
            route_name = route.get('name', '')
            lt_number = ''
            import re
            match = re.search(r'([A-Z]{3}\d{5})', route_name)
            if match:
                lt_number = match.group(1)
            
            if not lt_number:
                continue
            
            # PROVEN DEPOT/DAIRY CLASSIFICATION LOGIC
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
            
            if not dairy_stop:
                continue
            
            # PROVEN STATUS DETERMINATION LOGIC
            status = "Scheduled"
            dairy_arrival_mst = ""
            dairy_departure_mst = ""
            depot_departure_mst = ""
            
            if dairy_stop:
                dairy_state = dairy_stop.get('state', '')
                
                # Convert times to MST for display - PROVEN WORKING LOGIC
                if dairy_stop.get('actualArrivalTime'):
                    dairy_arrival_utc = datetime.fromisoformat(dairy_stop['actualArrivalTime'].replace('Z', '+00:00'))
                    dairy_arrival_mst = dairy_arrival_utc.astimezone(mst).isoformat()
                
                if dairy_stop.get('actualDepartureTime'):
                    dairy_departure_utc = datetime.fromisoformat(dairy_stop['actualDepartureTime'].replace('Z', '+00:00'))
                    dairy_departure_mst = dairy_departure_utc.astimezone(mst).isoformat()
                
                if depot_stop and depot_stop.get('actualDepartureTime'):
                    depot_departure_utc = datetime.fromisoformat(depot_stop['actualDepartureTime'].replace('Z', '+00:00'))
                    depot_departure_mst = depot_departure_utc.astimezone(mst).isoformat()
                
                # PROVEN BUSINESS LOGIC: Only care about route status UP TO DAIRY
                if dairy_state == 'departed':
                    status = "Completed"  # ✅ LEFT DAIRY = ROUTE COMPLETE (ignore processors)
                elif dairy_state == 'arrived':
                    status = "Filling Tank"  # 🥛 AT DAIRY = FILLING TANK
                elif dairy_state == 'skipped':
                    # Check if we've left depot (en route to dairy)
                    if depot_stop and depot_stop.get('state') == 'departed':
                        status = "En Route"  # 🚛 LEFT DEPOT, TRAVELING TO DAIRY
                    else:
                        status = "Scheduled"  # 📅 HASN'T STARTED YET
                else:
                    # Default logic if state is unclear
                    if depot_stop and depot_stop.get('state') == 'departed':
                        status = "En Route"  # 🚛 LEFT DEPOT, TRAVELING TO DAIRY
            
            # Extract dairy name from dairy stop
            dairy_name = "Unknown"
            if dairy_stop:
                dairy_name = dairy_stop.get('name', 'Unknown')
            
            # Get route times (convert to MST)
            actual_start_mst = ""
            if route.get('actualRouteStartTime'):
                start_utc = datetime.fromisoformat(route['actualRouteStartTime'].replace('Z', '+00:00'))
                actual_start_mst = start_utc.astimezone(mst).isoformat()
            
            # STORE DATA IN SAME FORMAT AS WORKING SCRIPT
            samsara_routes_map[lt_number] = {
                'samsara_route_id': route.get('id'),
                'route_name': route_name,
                'dairy_name': dairy_name,
                'samsara_status': status,
                'dairy_state': dairy_stop.get('state', '') if dairy_stop else '',
                'depot_state': depot_stop.get('state', '') if depot_stop else '',
                'route_start_time': actual_start_mst,
                'dairy_arrival_time': dairy_arrival_mst,
                'dairy_departure_time': dairy_departure_mst,
                'depot_departure_time': depot_departure_mst,
                'driver_name': route.get('driver', {}).get('name', 'Unknown')
            }
            
            print(f"    - ✅ Mapped LT#{lt_number}: {status} (PROVEN logic)")
            
        print(f"Successfully mapped {len(samsara_routes_map)} routes using PROVEN working logic")
        return samsara_routes_map
        
    except requests.exceptions.RequestException as e:
        print(f"Warning: Could not fetch Samsara routes: {e}")
        return {}

def main():
    """Main function to generate the daily routes report."""
    parser = argparse.ArgumentParser(description="Generate a daily routes report.")
    parser.add_argument("--date", default=date.today().strftime("%Y-%m-%d"), help="Date in YYYY-MM-DD format.")
    parser.add_argument("--dairy", help="Filter for a specific dairy name.")
    args = parser.parse_args()
    
    print(f"=== DEBUG: Fetching routes for TARGET DATE: {args.date} ===")
    
    samsara_locations = get_all_samsara_locations()
    if samsara_locations is None:
        return

    # Step 1: Get Samsara routes data for real-time enhancement
    print("Fetching Samsara routes data for real-time status...")
    samsara_routes_map = get_samsara_routes_data(days_back=7, target_date=args.date)
    
    # DEBUG: Print Samsara route details with dates
    print(f"\n=== SAMSARA ROUTES DEBUG ({len(samsara_routes_map)} routes) ===")
    for lt_num, route_data in list(samsara_routes_map.items())[:10]:  # Show first 10
        route_start = route_data.get('route_start_time', 'N/A')
        print(f"  Samsara LT#{lt_num}: Start={route_start}, Status={route_data.get('samsara_status')}")
    if len(samsara_routes_map) > 10:
        print(f"  ... and {len(samsara_routes_map) - 10} more routes")
    
    # Step 2: Get Milk Movement data
    summaries = get_load_summaries(args.date)
    if not summaries:
        print("Could not fetch pickup data.")
        return
    
    # DEBUG: Print MM route details with dates
    print(f"\n=== MILK MOVEMENT ROUTES DEBUG ({len(summaries)} routes) ===")
    for i, summary in enumerate(summaries[:10]):  # Show first 10
        lt_num = summary.get('invoice_number', 'N/A')
        pickup_date = summary.get('pickup_date', 'N/A')
        producer = summary.get('producer_name', 'N/A')
        print(f"  MM LT#{lt_num}: Date={pickup_date}, Dairy={producer}")
    if len(summaries) > 10:
        print(f"  ... and {len(summaries) - 10} more routes")
    
    # Step 3: Enhance MM data with Samsara real-time status
    print(f"\n=== MATCHING ATTEMPT ===")
    enhanced_summaries = enhance_mm_data_with_samsara(summaries, samsara_routes_map)
    
    # Step 4: Generate routes report with enhanced data
    print("Generating routes report with Samsara-enhanced data...")
    report = generate_routes_report(enhanced_summaries, samsara_locations, args.dairy)
    
    if not report.empty:
        title = f"Daily Routes for {args.dairy}" if args.dairy else "All Daily Routes"
        print(f"\n--- {title} on {args.date} ---")
        print(report.to_string())
        print("\n-------------------------------------------------\n")
    else:
        print("No matching routes found to display.")

if __name__ == "__main__":
    main() 