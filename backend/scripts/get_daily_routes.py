import requests
import os
import argparse
import pandas as pd
from datetime import date, datetime, timedelta
import json
import math

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
        return None

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

        # Determine Status from Geofence data
        if pd.notna(row['dropoff_date']):
            status = 'Completed'
        elif pd.notna(row['geofence_enter_time']):
            status = 'Arrived'
        else:
            status = 'En Route'
        
        print(f"  - Geofence Status: '{status}'")

        # Get route information from the data
        route_info = row.get('route_number', row.get('route_name', row.get('invoice_number', 'N/A')))

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
        
        report_data.append({
            'Start Time': pd.to_datetime(row['pickup_date']).strftime('%H:%M'),
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

def main():
    """Main function to generate the daily routes report."""
    parser = argparse.ArgumentParser(description="Generate a daily routes report.")
    parser.add_argument("--date", default=date.today().strftime("%Y-%m-%d"), help="Date in YYYY-MM-DD format.")
    parser.add_argument("--dairy", help="Filter for a specific dairy name.")
    args = parser.parse_args()
    
    # get_all_samsara_vehicles() # Diagnostic function, no longer needed.

    samsara_locations = get_all_samsara_locations()
    if samsara_locations is None:
        return

    summaries = get_load_summaries(args.date)
    if summaries:
        report = generate_routes_report(summaries, samsara_locations, args.dairy)
        if not report.empty:
            title = f"Daily Routes for {args.dairy}" if args.dairy else "All Daily Routes"
            print(f"\n--- {title} on {args.date} ---")
            print(report.to_string())
            print("\n-------------------------------------------------\n")
        else:
            print("No matching routes found to display.")
    else:
        print("Could not fetch pickup data.")

if __name__ == "__main__":
    main() 