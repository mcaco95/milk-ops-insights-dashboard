#!/usr/bin/env python3
"""
Debug the calculate_tank_status function to see why it's returning None
"""

import sys
import os

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status

def debug_calculation():
    """Debug the calculate_tank_status function"""
    print("=== DEBUGGING CALCULATE_TANK_STATUS ===\n")
    
    submissions = get_volume_submissions(hours_back=24)
    print(f"Found {len(submissions)} raw submissions")
    
    # Parse submissions
    current_data = []
    for submission in submissions:
        parsed = parse_submission_volumes(submission)
        if parsed.get('dairy') and parsed.get('volumes'):
            current_data.append(parsed)
    
    print(f"Found {len(current_data)} parsed submissions with data")
    
    # Show T&K submissions specifically
    tk_data = [d for d in current_data if 'T&K' in d.get('dairy', '')]
    print(f"Found {len(tk_data)} T&K submissions:")
    
    for i, tk in enumerate(tk_data[:3]):
        print(f"  {i+1}. {tk['dairy']}:")
        print(f"     Volumes: {tk['volumes']}")
        print(f"     Milking into: {tk.get('milking_into')}")
        print(f"     Timestamp: {tk.get('timestamp')}")
    
    print(f"\n=== CALLING CALCULATE_TANK_STATUS ===")
    
    # Call calculate_tank_status with debug
    try:
        tank_statuses = calculate_tank_status(current_data)
        print(f"Function returned: {type(tank_statuses)}")
        print(f"Keys: {list(tank_statuses.keys())}")
        
        # Look at T&K results specifically
        for dairy_name, tanks in tank_statuses.items():
            if 'T&K' in dairy_name:
                print(f"\n{dairy_name}:")
                for tank_name, tank_info in tanks.items():
                    print(f"  {tank_name}:")
                    print(f"    current_volume: {tank_info.get('current_volume')}")
                    print(f"    status: {tank_info.get('status')}")
                    print(f"    capacity: {tank_info.get('capacity')}")
                    print(f"    last_update: {tank_info.get('last_update')}")
                    print(f"    is_being_filled: {tank_info.get('is_being_filled')}")
        
    except Exception as e:
        print(f"Error calling calculate_tank_status: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_calculation() 