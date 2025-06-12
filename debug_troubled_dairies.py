#!/usr/bin/env python3
"""
Debug Script for Troubled Dairies - LOCAL VERSION

Focuses specifically on Arizona Dairy, D&I Coolidge (805), and D&I Stanfield (716)
to show their raw data from forms. No database connection required.
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status

def debug_troubled_dairies():
    """Debug the three specific dairies having issues."""
    print("🔍 DEBUGGING TROUBLED DAIRIES - LOCAL VERSION")
    print("=" * 60)
    
    # The three troubled dairies
    troubled_dairies = [
        "Arizona Dairy",
        "D&I Coolidge (805)", 
        "D&I Stanfield (716)"
    ]
    
    # Their database IDs (for reference)
    db_mappings = {
        "Arizona Dairy": "az_dairy",
        "D&I Coolidge (805)": "d_i_dairy",
        "D&I Stanfield (716)": "d_i_holsteins"
    }
    
    print("\n1. RAW FORM SUBMISSIONS (Last 48 Hours)")
    print("-" * 40)
    
    try:
        # Get form submissions
        submissions = get_volume_submissions(hours_back=48)
        print(f"Total submissions found: {len(submissions)}")
        
        # First, let's see ALL dairy names in submissions to understand the issue
        all_dairy_names = set()
        for submission in submissions:
            try:
                parsed = parse_submission_volumes(submission)
                dairy_name = parsed.get('dairy')
                if dairy_name:
                    all_dairy_names.add(dairy_name)
            except Exception as e:
                continue
        
        print(f"\nAll unique dairy names found in submissions:")
        for name in sorted(all_dairy_names):
            print(f"  - '{name}'")
        
        print(f"\nNow checking specifically for our troubled dairies:")
        
        for dairy_name in troubled_dairies:
            print(f"\n🏭 {dairy_name}")
            print("=" * len(dairy_name) + "===")
            
            dairy_submissions = []
            for submission in submissions:
                try:
                    parsed = parse_submission_volumes(submission)
                    parsed_name = parsed.get('dairy', '').strip()
                    if parsed_name == dairy_name:
                        dairy_submissions.append((submission, parsed))
                except Exception as e:
                    continue
            
            print(f"Found {len(dairy_submissions)} submissions for '{dairy_name}'")
            
            if dairy_submissions:
                print("\nRAW SUBMISSION DATA:")
                for i, (sub, parsed) in enumerate(dairy_submissions, 1):
                    print(f"\n  Submission #{i}:")
                    print(f"    ID: {sub.get('id', 'N/A')}")
                    print(f"    Created At: {sub.get('createdAtTime', 'N/A')}")
                    print(f"    Submitted At: {sub.get('submittedAtTime', 'N/A')}")
                    print(f"    Parsed Dairy: '{parsed.get('dairy', 'N/A')}'")
                    print(f"    Parsed Volumes: {parsed.get('volumes', 'N/A')}")
                    print(f"    Milking Into: {parsed.get('milking_into', 'N/A')}")
                    print(f"    Pulled From: {parsed.get('pulled_from', 'N/A')}")
                    
                    # Show raw fields for debugging
                    print(f"    Raw Fields:")
                    fields = sub.get('fields', [])
                    for field in fields:
                        label = field.get('label', '')
                        field_type = field.get('type', '')
                        print(f"      - {label} ({field_type}): {field}")
            else:
                print("  ❌ NO SUBMISSIONS FOUND")
                
                # Let's check if there are similar names
                print("  🔍 Checking for similar dairy names...")
                for name in all_dairy_names:
                    if any(word in name.lower() for word in dairy_name.lower().split()):
                        print(f"    Similar: '{name}'")
    
    except Exception as e:
        print(f"❌ Error fetching form submissions: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n\n2. TANK STATUS CALCULATION TEST")
    print("-" * 40)
    
    try:
        # Get submissions and calculate tank status
        submissions = get_volume_submissions(hours_back=48)
        
        # Parse submissions to get current data list
        current_data = []
        for submission in submissions:
            parsed = parse_submission_volumes(submission)
            if parsed.get('dairy') and parsed.get('volumes'):
                current_data.append(parsed)
        
        print(f"Parsed {len(current_data)} submissions with dairy and volume data")
        
        # Show what dairies we have data for
        dairy_names_with_data = set()
        for data in current_data:
            dairy_names_with_data.add(data['dairy'])
        
        print(f"\nDairies with volume data:")
        for name in sorted(dairy_names_with_data):
            print(f"  - '{name}'")
        
        # Calculate tank statuses
        tank_statuses = calculate_tank_status(current_data)
        
        print(f"\nTank status calculation results:")
        for dairy_name in troubled_dairies:
            if dairy_name in tank_statuses:
                print(f"  ✅ {dairy_name}: HAS CALCULATED DATA")
                tanks = tank_statuses[dairy_name]
                for tank_name, tank_info in tanks.items():
                    volume = tank_info.get('current_volume', 0)
                    print(f"    - {tank_name}: {volume} lbs")
            else:
                print(f"  ❌ {dairy_name}: NO CALCULATED DATA")
        
    except Exception as e:
        print(f"❌ Error in tank status calculation: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n\n3. SUMMARY")
    print("-" * 40)
    
    print("\nThis script shows:")
    print("- All dairy names found in form submissions")
    print("- Raw submission data for the three troubled dairies")
    print("- Whether tank status calculation works for them")
    print("\nIf submissions are found but tank calculation fails,")
    print("the issue is in the calculation logic.")
    print("If no submissions are found, the issue is in dairy name matching.")
    
    print("\n✅ DEBUG COMPLETE")

if __name__ == "__main__":
    debug_troubled_dairies() 