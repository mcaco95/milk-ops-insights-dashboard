#!/usr/bin/env python3
"""
Force Update Tank Data Script

This is a one-off script to bypass any potential mapping or Docker image issues
and directly insert the correct tank data into the database.
"""

import sys
import os
import psycopg2
from datetime import datetime

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status
from scripts.populate_tanks_data import get_db_connection # Reuse connection logic

def force_update():
    """Calculates tank status and forces an update for specific dairies."""
    print("🚀 STARTING FORCE UPDATE SCRIPT 🚀")

    # This is the map we know is correct from the form submissions
    hardcoded_map = {
        "Arizona Dairy": "az_dairy",
        "D&I Coolidge (805)": "d_i_dairy",
        "D&I Stanfield (716)": "d_i_holsteins"
    }
    
    try:
        # 1. Get the data from forms
        print("\n[Step 1] Fetching form submissions from the last 48 hours...")
        submissions = get_volume_submissions(hours_back=48)
        print(f"✅ Found {len(submissions)} form submissions.")

        # 2. Calculate tank statuses
        print("\n[Step 2] Calculating tank statuses from form data...")
        current_data = []
        for submission in submissions:
            parsed = parse_submission_volumes(submission)
            if parsed.get('dairy') and parsed.get('volumes'):
                current_data.append(parsed)
        
        tank_statuses = calculate_tank_status(current_data)
        print("✅ Tank status calculation complete.")

        # 3. Connect to the database and force update
        print("\n[Step 3] Connecting to the database and forcing update...")
        updated_count = 0
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Loop through the dairies we want to force-update
                for dairy_name_from_config, dairy_id in hardcoded_map.items():
                    
                    if dairy_name_from_config in tank_statuses:
                        print(f"\nProcessing '{dairy_name_from_config}' (ID: {dairy_id})")
                        tanks = tank_statuses[dairy_name_from_config]

                        for tank_name, tank_info in tanks.items():
                            current_volume = tank_info.get('current_volume', 0) or 0
                            
                            # We only care about updating tanks that have data
                            if current_volume > 0:
                                # Get other info
                                base_volume = tank_info.get('base_volume_lbs', 0)
                                predicted_added = tank_info.get('predicted_added_lbs', 0)
                                capacity = tank_info.get('capacity', 0)
                                time_to_full = tank_info.get('time_to_full_hours')
                                is_milking = tank_info.get('is_milking') or False
                                last_pulled_at_str = tank_info.get('last_pulled_at')
                                last_pulled_at = datetime.fromisoformat(last_pulled_at_str) if last_pulled_at_str else None
                                
                                # --- Wash Status Logic (copied from main script) ---
                                cur.execute("SELECT current_volume_lbs, wash_started_at FROM tanks_data WHERE dairy_id = %s AND tank_name = %s", (dairy_id, tank_name))
                                result = cur.fetchone()
                                previous_volume = result[0] if result else 0
                                existing_wash_started_at = result[1] if result else None
                                new_wash_started_at = existing_wash_started_at
                                if current_volume < 5000 and previous_volume >= 5000:
                                    new_wash_started_at = datetime.utcnow()
                                is_washing = new_wash_started_at is not None
                                
                                # Simplified barn logic
                                if '[' in dairy_name_from_config and ']' in dairy_name_from_config:
                                    barn_name = dairy_name_from_config.split('[')[1].split(']')[0]
                                else:
                                    barn_name = "Main Barn"
                                
                                print(f"  - Updating tank '{tank_name}' with volume {current_volume}...")
                                
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
                                    dairy_id, barn_name, tank_name, current_volume, base_volume,
                                    predicted_added, capacity, time_to_full, is_milking, is_washing,
                                    last_pulled_at, new_wash_started_at, datetime.utcnow()
                                ))
                                updated_count += 1
                            else:
                                print(f"  - Skipping tank '{tank_name}' (volume is 0).")
                    else:
                        print(f"No data calculated for '{dairy_name_from_config}'. Skipping.")

            conn.commit()
            print(f"\n✅ DATABASE COMMIT SUCCESSFUL. Forced update for {updated_count} tank records.")

    except Exception as e:
        print(f"\n❌ AN ERROR OCCURRED: {str(e)}")
        
if __name__ == "__main__":
    force_update() 