#!/usr/bin/env python3
"""
Debug Populate Process Script

This script traces exactly what happens to the troubled dairies
during the populate_tanks_data process to find where real data becomes 0.
"""

import sys
import os
import psycopg2
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status
from scripts.populate_tanks_data import get_db_connection, get_dairy_mapping

def debug_populate_process():
    """Debug the exact populate process for troubled dairies."""
    print("🔍 DEBUGGING POPULATE PROCESS")
    print("=" * 60)
    
    # The three troubled dairies
    troubled_dairies = ["Arizona Dairy", "D&I Coolidge (805)", "D&I Stanfield (716)"]
    
    try:
        print("\n1. GETTING FORM SUBMISSIONS")
        print("-" * 40)
        
        submissions = get_volume_submissions(hours_back=48)
        print(f"Total submissions: {len(submissions)}")
        
        print("\n2. PARSING SUBMISSIONS")
        print("-" * 40)
        
        current_data = []
        troubled_parsed_data = {}
        
        for submission in submissions:
            parsed = parse_submission_volumes(submission)
            if parsed.get('dairy') and parsed.get('volumes'):
                current_data.append(parsed)
                
                # Track troubled dairies specifically
                if parsed.get('dairy') in troubled_dairies:
                    dairy_name = parsed.get('dairy')
                    if dairy_name not in troubled_parsed_data:
                        troubled_parsed_data[dairy_name] = []
                    troubled_parsed_data[dairy_name].append(parsed)
        
        print(f"Total parsed submissions with dairy and volumes: {len(current_data)}")
        
        print(f"\nTroubled dairy parsed data:")
        for dairy_name in troubled_dairies:
            if dairy_name in troubled_parsed_data:
                data_list = troubled_parsed_data[dairy_name]
                print(f"  ✅ {dairy_name}: {len(data_list)} parsed submissions")
                for i, data in enumerate(data_list):
                    print(f"    [{i}] Volumes: {data.get('volumes', {})}")
                    print(f"    [{i}] Milking: {data.get('milking_into', 'N/A')}")
                    print(f"    [{i}] Timestamp: {data.get('timestamp', 'N/A')}")
            else:
                print(f"  ❌ {dairy_name}: NO PARSED DATA")
        
        print("\n3. CALCULATING TANK STATUS")
        print("-" * 40)
        
        tank_statuses = calculate_tank_status(current_data)
        print(f"Tank statuses calculated for {len(tank_statuses)} dairies")
        
        print(f"\nTroubled dairy tank statuses:")
        for dairy_name in troubled_dairies:
            if dairy_name in tank_statuses:
                tanks = tank_statuses[dairy_name]
                print(f"  ✅ {dairy_name}: {len(tanks)} tanks calculated")
                for tank_name, tank_info in tanks.items():
                    current_vol = tank_info.get('current_volume', 0)
                    base_vol = tank_info.get('base_volume_lbs', 0)
                    predicted = tank_info.get('predicted_added_lbs', 0)
                    print(f"    - {tank_name}:")
                    print(f"      Current Volume: {current_vol}")
                    print(f"      Base Volume: {base_vol}")
                    print(f"      Predicted Added: {predicted}")
                    print(f"      Full Tank Info: {tank_info}")
            else:
                print(f"  ❌ {dairy_name}: NO TANK STATUS CALCULATED")
        
        print("\n4. TESTING DATABASE MAPPING")
        print("-" * 40)
        
        with get_db_connection() as conn:
            dairy_mapping = get_dairy_mapping(conn)
            
            for dairy_name in troubled_dairies:
                if dairy_name in dairy_mapping:
                    dairy_id = dairy_mapping[dairy_name]
                    print(f"  ✅ {dairy_name} -> {dairy_id}")
                else:
                    print(f"  ❌ {dairy_name} -> NO MAPPING")
        
        print("\n5. SIMULATING DATABASE INSERTION LOGIC")
        print("-" * 40)
        
        with get_db_connection() as conn:
            dairy_mapping = get_dairy_mapping(conn)
            
            for dairy_name_from_script, tanks in tank_statuses.items():
                if dairy_name_from_script not in troubled_dairies:
                    continue
                    
                print(f"\nProcessing {dairy_name_from_script}:")
                
                # This is the exact logic from populate_tanks_data.py
                dairy_id = dairy_mapping.get(dairy_name_from_script)
                if not dairy_id:
                    print(f"  ❌ No mapping found for '{dairy_name_from_script}'")
                    continue
                
                print(f"  ✅ Mapped to dairy_id: {dairy_id}")
                
                # Barn name logic
                if '[' in dairy_name_from_script and ']' in dairy_name_from_script:
                    barn_name = dairy_name_from_script.split('[')[1].split(']')[0]
                else:
                    barn_name = "Main Barn"
                
                print(f"  Barn name: {barn_name}")
                
                for tank_name, tank_info in tanks.items():
                    current_volume = tank_info.get('current_volume', 0) or 0
                    print(f"  Tank {tank_name}:")
                    print(f"    Raw current_volume from tank_info: {tank_info.get('current_volume')}")
                    print(f"    Processed current_volume: {current_volume}")
                    
                    if current_volume > 0:
                        print(f"    ✅ Would insert {current_volume} lbs")
                    else:
                        print(f"    ❌ Would insert 0 lbs (PROBLEM HERE!)")
                        print(f"    Full tank_info: {tank_info}")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ DEBUG COMPLETE")

if __name__ == "__main__":
    debug_populate_process() 