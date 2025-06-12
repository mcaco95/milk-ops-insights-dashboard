#!/usr/bin/env python3
"""
Debug Fix Script Issue

This script debugs why the fix_troubled_dairies.py script isn't finding
tank statuses for the troubled dairies.
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status

def debug_fix_script():
    """Debug the fix script issue."""
    print("🔍 DEBUGGING FIX SCRIPT ISSUE")
    print("=" * 60)
    
    # The exact 3 dairies that are failing
    troubled_mappings = {
        "Arizona Dairy": "az_dairy",
        "D&I Coolidge (805)": "d_i_dairy", 
        "D&I Stanfield (716)": "d_i_holsteins"
    }
    
    print(f"Target dairies: {list(troubled_mappings.keys())}")
    
    try:
        # Get form submissions and calculate tank status (same as fix script)
        print("\n1. Getting form submissions...")
        submissions = get_volume_submissions(hours_back=48)
        print(f"Found {len(submissions)} form submissions")
        
        print("\n2. Parsing submissions...")
        current_data = []
        for submission in submissions:
            parsed = parse_submission_volumes(submission)
            if parsed.get('dairy') and parsed.get('volumes'):
                current_data.append(parsed)
        
        print(f"Parsed {len(current_data)} submissions with dairy and volume data")
        
        # Show unique dairy names from parsed data
        unique_dairies = set(item['dairy'] for item in current_data)
        print(f"\nUnique dairy names from parsed data:")
        for dairy in sorted(unique_dairies):
            print(f"  '{dairy}'")
        
        print("\n3. Calculating tank statuses...")
        tank_statuses = calculate_tank_status(current_data)
        print(f"Tank statuses calculated for {len(tank_statuses)} dairies")
        
        print(f"\nDairies with tank statuses:")
        for dairy_name in sorted(tank_statuses.keys()):
            print(f"  '{dairy_name}': {len(tank_statuses[dairy_name])} tanks")
        
        print("\n4. Checking troubled dairies...")
        for dairy_name in troubled_mappings.keys():
            if dairy_name in tank_statuses:
                tanks = tank_statuses[dairy_name]
                print(f"✅ {dairy_name}: {len(tanks)} tanks calculated")
                for tank_name, tank_info in tanks.items():
                    volume = tank_info.get('current_volume', 0)
                    print(f"   - {tank_name}: {volume} lbs")
            else:
                print(f"❌ {dairy_name}: NO tank status calculated")
                
                # Check if there's a similar name
                for calculated_dairy in tank_statuses.keys():
                    if dairy_name.lower() in calculated_dairy.lower() or calculated_dairy.lower() in dairy_name.lower():
                        print(f"   🔍 Similar name found: '{calculated_dairy}'")
        
        print("\n5. Checking raw parsed data for troubled dairies...")
        for dairy_name in troubled_mappings.keys():
            matching_submissions = [item for item in current_data if item['dairy'] == dairy_name]
            print(f"{dairy_name}: {len(matching_submissions)} matching submissions")
            if matching_submissions:
                sample = matching_submissions[0]
                print(f"  Sample: {sample['volumes']}")
        
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_fix_script() 