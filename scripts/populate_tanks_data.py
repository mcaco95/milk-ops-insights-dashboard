#!/usr/bin/env python3
"""
Tank Data Population Script
Runs the tank level dashboard logic and stores results in the database.
Should be run periodically (e.g., every 10 minutes) via cron/scheduler.
"""

import sys
import os
import psycopg2
from datetime import datetime
import json

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status, DAIRY_CONFIG

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
        cur.execute("SELECT id, tank_dashboard_names FROM dairies")
        for row in cur.fetchall():
            dairy_id, names = row
            if names:
                # Handle case where psycopg2 returns array as a string like '{"Name 1","Name 2"}'
                if isinstance(names, str):
                    # Remove curly braces, split by comma, and strip quotes/whitespace
                    parsed_names = [n.strip().strip('"') for n in names.strip('{}').split(',')]
                elif isinstance(names, list):
                    # If it's already a list, use it directly
                    parsed_names = names
                else:
                    parsed_names = []

                for name in parsed_names:
                    if name: # Ensure name is not an empty string
                        mapping[name] = dairy_id
    return mapping

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def populate_tanks_data():
    """Populate tanks data table from tank level dashboard"""
    try:
        print("Starting tank data population...")
        
        with get_db_connection() as conn:
            # Get the centralized dairy mapping
            dairy_name_mapping = get_dairy_mapping(conn)
            if not dairy_name_mapping:
                print("FATAL: Could not load dairy mappings from the database.")
                return

            # Get tank status data using the updated calculation logic
            submissions = get_volume_submissions(hours_back=48) # Increased to 48h for better wash status tracking
            print(f"Found {len(submissions)} form submissions in the last 48 hours")
            
            # Parse submissions to get current data list
            current_data = []
            for submission in submissions:
                parsed = parse_submission_volumes(submission)
                if parsed.get('dairy') and parsed.get('volumes'):
                    current_data.append(parsed)
            
            # Calculate all available tank statuses
            tank_statuses = calculate_tank_status(current_data)
            
            with conn.cursor() as cur:
                insert_count = 0
                
                # TEMPORARY HARDCODED MAPPING FOR DEBUGGING
                hardcoded_map = {
                    "Arizona Dairy": "az_dairy",
                    "D&I Coolidge (805)": "d_i_dairy",
                    "D&I Stanfield (716)": "d_i_holsteins"
                }
                
                for dairy_name_from_script, tanks in tank_statuses.items():
                    # Map dairy name to database ID
                    dairy_id = None
                    if dairy_name_from_script in hardcoded_map:
                        dairy_id = hardcoded_map[dairy_name_from_script]
                        print(f"INFO: Using hardcoded map for '{dairy_name_from_script}' -> '{dairy_id}'")
                    else:
                        dairy_id = dairy_name_mapping.get(dairy_name_from_script)

                    if not dairy_id:
                        print(f"Warning: No mapping found for dairy '{dairy_name_from_script}' from script.")
                        continue
                    
                    if '[' in dairy_name_from_script and ']' in dairy_name_from_script:
                        barn_name = dairy_name_from_script.split('[')[1].split(']')[0]
                    else:
                        barn_name = "Main Barn"
                    
                    for tank_name, tank_info in tanks.items():
                        # Get all the new detailed values
                        current_volume = tank_info.get('current_volume', 0) or 0
                        base_volume = tank_info.get('base_volume_lbs', 0)
                        predicted_added = tank_info.get('predicted_added_lbs', 0)
                        capacity = tank_info.get('capacity', 0)
                        time_to_full = tank_info.get('time_to_full_hours')
                        is_milking = tank_info.get('is_milking') or False  # Ensure None becomes False
                        last_pulled_at_str = tank_info.get('last_pulled_at')
                        last_pulled_at = datetime.fromisoformat(last_pulled_at_str) if last_pulled_at_str else None

                        # --- Wash Status Logic ---
                        cur.execute(
                            "SELECT current_volume_lbs, wash_started_at FROM tanks_data WHERE dairy_id = %s AND tank_name = %s",
                            (dairy_id, tank_name)
                        )
                        result = cur.fetchone()
                        
                        previous_volume = result[0] if result else 0
                        existing_wash_started_at = result[1] if result else None
                        new_wash_started_at = existing_wash_started_at

                        # Timer only resets when crossing from ≥5k to <5k (new wash cycle)
                        if current_volume < 5000 and previous_volume >= 5000:
                            new_wash_started_at = datetime.utcnow()
                        # Timer keeps running regardless of volume until next wash cycle
                        
                        # Legacy wash flag, can be removed later
                        is_washing = new_wash_started_at is not None

                        # Upsert all data into the database
                        cur.execute("""
                            INSERT INTO tanks_data 
                            (dairy_id, barn_name, tank_name, current_volume_lbs, base_volume_lbs, predicted_added_lbs, capacity_lbs, time_to_full_hours, is_milking, is_washing, last_pulled_at, wash_started_at, last_updated)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (dairy_id, barn_name, tank_name) 
                            DO UPDATE SET 
                                current_volume_lbs = EXCLUDED.current_volume_lbs,
                                base_volume_lbs = EXCLUDED.base_volume_lbs,
                                predicted_added_lbs = EXCLUDED.predicted_added_lbs,
                                capacity_lbs = EXCLUDED.capacity_lbs,
                                time_to_full_hours = EXCLUDED.time_to_full_hours,
                                is_milking = EXCLUDED.is_milking,
                                is_washing = EXCLUDED.is_washing,
                                last_pulled_at = EXCLUDED.last_pulled_at,
                                wash_started_at = EXCLUDED.wash_started_at,
                                last_updated = EXCLUDED.last_updated
                        """, (
                            dairy_id,
                            barn_name,
                            tank_name,
                            current_volume,
                            base_volume,
                            predicted_added,
                            capacity,
                            time_to_full,
                            is_milking,
                            is_washing,
                            last_pulled_at,
                            new_wash_started_at,
                            datetime.utcnow()
                        ))
                        insert_count += 1
                
                conn.commit()
                print(f"Successfully inserted/updated {insert_count} tank records")
        
    except Exception as e:
        print(f"Error populating tank data: {str(e)}")
        raise

if __name__ == "__main__":
    populate_tanks_data() 