#!/usr/bin/env python3
"""
Routes Data Population Script
Runs the FULL daily routes logic and stores REAL results in the database.
Should be run daily via cron/scheduler.
"""

import sys
import os
import psycopg2
from datetime import datetime, date, timedelta
import json

# Add parent directory to import our routes script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_daily_routes import get_load_summaries, get_all_samsara_locations, generate_routes_report, get_vehicle_location_and_speed, get_combined_routes_data

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "dairy_operations"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

def get_dairy_mapping(conn):
    """Fetches the dairy name mappings from the database."""
    mapping = {}
    with conn.cursor() as cur:
        # Fetch from milk_movement_names for routes
        cur.execute("SELECT id, milk_movement_names FROM dairies")
        for row in cur.fetchall():
            dairy_id, names = row
            if names:
                for name in names:
                    mapping[name] = dairy_id
    return mapping

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def populate_routes_data(target_date=None):
    """Populate routes data table using FULL daily routes logic INCLUDING scheduled routes"""
    if target_date is None:
        target_date = date.today()
    
    try:
        print(f"Starting FULL route data population (pickups + schedules) for {target_date}...")
        
        with get_db_connection() as conn:
            # Get the centralized dairy mapping
            dairy_name_mapping = get_dairy_mapping(conn)
            if not dairy_name_mapping:
                print("FATAL: Could not load dairy mappings from the database.")
                return

            # Get Samsara locations first
            print("Fetching Samsara locations...")
            samsara_locations = get_all_samsara_locations()
            if not samsara_locations:
                print("WARNING: Could not fetch Samsara locations. Route ETAs will be unavailable.")
            
            # Get COMBINED data (pickups + schedules) instead of just load summaries
            date_str = target_date.strftime("%Y-%m-%d")
            print(f"Fetching COMBINED route data (pickups + schedules) for {date_str}...")
            
            # Use the combined function that gets both pickups and schedules
            combined_data = get_combined_routes_data(date_str)
            
            if not combined_data:
                print(f"No combined route data found for {date_str}")
                return
            
            print(f"Found {len(combined_data)} total route records (pickups + schedules)")
            
            # Generate FULL routes report using the real logic
            print("Generating full routes report with real driver/truck/ETA data...")
            full_report = generate_routes_report(combined_data, samsara_locations)
            
            if full_report.empty:
                print("No route data generated from combined data")
                return
            
            print(f"Generated {len(full_report)} route records")
            print("\nRoute data preview:")
            print(full_report.to_string())
            
            # Insert real route data into database
            with conn.cursor() as cur:
                insert_count = 0
                
                for _, route_row in full_report.iterrows():
                    # Map dairy name to database ID
                    dairy_name = route_row['Dairy']
                    dairy_id = dairy_name_mapping.get(dairy_name)
                    
                    if not dairy_id:
                        print(f"Warning: No mapping found for dairy '{dairy_name}'")
                        continue
                    
                    # Parse start time into a full datetime
                    try:
                        start_time_str = route_row['Start Time']  # Format: "16:31"
                        start_hour, start_minute = map(int, start_time_str.split(':'))
                        estimated_arrival = datetime.combine(target_date, datetime.min.time().replace(hour=start_hour, minute=start_minute))
                        
                        # If it's a past time, assume next day (for late night routes)
                        if estimated_arrival.time().hour < 6:  # Routes after midnight
                            estimated_arrival = estimated_arrival + timedelta(days=1)
                    except:
                        estimated_arrival = None
                    
                    # Determine status
                    status_map = {
                        'Completed': 'completed',
                        'Arrived': 'active', 
                        'En Route': 'active',
                        'Unknown': 'scheduled'
                    }
                    status = status_map.get(route_row['Status'], 'scheduled')
                    
                    # Get real driver name and truck ID
                    driver_name = route_row.get('Driver', 'TBD')
                    truck_id = str(route_row.get('Truck #', 'TBD'))
                    route_number = str(route_row.get('Route', f"route_{insert_count}"))
                    
                    # Target location (tank info)
                    tank_info = route_row.get('Tank', '1')
                    target_location = f"{dairy_name} - Tank {tank_info}"
                    
                    # Get live vehicle location if truck is known
                    vehicle_location = None
                    if truck_id != 'TBD' and truck_id != 'Unknown':
                        try:
                            location, speed = get_vehicle_location_and_speed(truck_id)
                            if location:
                                # This is not used in the schema anymore, but we'll keep it for now
                                vehicle_location = json.dumps(location)
                                print(f"  - Got live location for truck {truck_id}: {location}")
                        except Exception as e:
                            print(f"  - Could not get location for truck {truck_id}: {str(e)}")
                    
                    # Insert route data with new columns
                    cur.execute("""
                        INSERT INTO routes_data
                        (
                            dairy_id, report_date, samsara_route_id, driver_name, truck_id, status, estimated_arrival,
                            start_date, route, dairy_name, tank, processor, lt_number, fairlife_number, tracking_link, 
                            last_updated
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (dairy_id, report_date, samsara_route_id, driver_name, truck_id)
                        DO UPDATE SET
                            status = EXCLUDED.status,
                            estimated_arrival = EXCLUDED.estimated_arrival,
                            start_date = EXCLUDED.start_date,
                            route = EXCLUDED.route,
                            dairy_name = EXCLUDED.dairy_name,
                            tank = EXCLUDED.tank,
                            processor = EXCLUDED.processor,
                            lt_number = EXCLUDED.lt_number,
                            fairlife_number = EXCLUDED.fairlife_number,
                            tracking_link = EXCLUDED.tracking_link,
                            last_updated = EXCLUDED.last_updated
                    """, (
                        dairy_id,
                        target_date,
                        route_row.get('Route', f"route_{insert_count}"),
                        driver_name if driver_name != 'Unknown' else 'TBD',
                        truck_id if truck_id != 'Unknown' else 'TBD',
                        status,
                        estimated_arrival,
                        route_row.get('Start Date'),
                        route_row.get('Route'),
                        route_row.get('Dairy'),
                        route_row.get('Tank'),
                        route_row.get('Processor'),
                        route_row.get('LT Number'),
                        route_row.get('Fairlife Number'),
                        route_row.get('Tracking Link'),
                        datetime.utcnow()
                    ))
                    insert_count += 1
                
                conn.commit()
                
                # Final success log
                print("\n" + "="*60)
                print(f"✅ SUCCESS: Saved {insert_count} route records to the database for {target_date}.")
                print("="*60 + "\n")
        
    except Exception as e:
        print(f"❌ Error populating route data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate REAL routes data for a specific date")
    parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD format (default: today)")
    args = parser.parse_args()
    
    target_date = None
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)
    
    populate_routes_data(target_date) 