#!/usr/bin/env python3
"""
Debug Tank Mapping Script
Check what dairy names are coming from Samsara forms vs what's expected
"""

import sys
import os
from collections import defaultdict

# Add current directory to import tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status, DAIRY_CONFIG

def debug_tank_mapping():
    """Debug tank data mapping issues"""
    
    print("🔍 DEBUGGING TANK MAPPING")
    print("="*60)
    
    # 1. Check what's in DAIRY_CONFIG
    print("\n1. DAIRY_CONFIG Keys:")
    for dairy_name in sorted(DAIRY_CONFIG.keys()):
        tank_count = len(DAIRY_CONFIG[dairy_name]['tanks'])
        print(f"   - {dairy_name} ({tank_count} tanks)")
    
    # 2. Get form submissions
    print(f"\n2. Form Submissions (last 48h):")
    submissions = get_volume_submissions(hours_back=48)
    print(f"   Found {len(submissions)} total submissions")
    
    # 3. Parse submissions and see dairy names
    print(f"\n3. Parsed Dairy Names from Forms:")
    parsed_data = []
    dairy_counts = defaultdict(int)
    
    for submission in submissions:
        parsed = parse_submission_volumes(submission)
        parsed_data.append(parsed)
        
        if parsed.get('dairy'):
            dairy_counts[parsed['dairy']] += 1
    
    for dairy_name, count in sorted(dairy_counts.items()):
        print(f"   - '{dairy_name}' ({count} submissions)")
    
    # 4. Check for missing dairies
    print(f"\n4. Missing Dairy Analysis:")
    problem_dairies = ['Arizona Dairy', 'AZ Dairy', 'Belmont', 'D&I Coolidge (805)', 'D&I Dairy', 'D&I Stanfield (716)', 'D & I Holsteins']
    
    for problem_dairy in problem_dairies:
        if problem_dairy in dairy_counts:
            print(f"   ✅ '{problem_dairy}' - Found {dairy_counts[problem_dairy]} submissions")
        else:
            print(f"   ❌ '{problem_dairy}' - NO SUBMISSIONS FOUND")
    
    # 5. Run tank status calculation
    print(f"\n5. Tank Status Calculation:")
    tank_statuses = calculate_tank_status(parsed_data)
    
    for dairy_name, tanks in tank_statuses.items():
        has_data = any(tank.get('current_volume', 0) > 0 for tank in tanks.values())
        status = "✅ HAS DATA" if has_data else "❌ NO DATA"
        print(f"   - {dairy_name}: {status}")
    
    # 6. Sample form data for problem dairies
    print(f"\n6. Sample Form Data:")
    for dairy_name in ['Arizona Dairy', 'Belmont', 'D&I Coolidge (805)', 'D&I Stanfield (716)']:
        matching_submissions = [p for p in parsed_data if p.get('dairy') == dairy_name]
        if matching_submissions:
            latest = matching_submissions[0]
            print(f"   {dairy_name}:")
            print(f"     Volumes: {latest.get('volumes', {})}")
            print(f"     Milking Into: {latest.get('milking_into')}")
            print(f"     Timestamp: {latest.get('timestamp')}")
        else:
            print(f"   {dairy_name}: No form submissions")

if __name__ == "__main__":
    debug_tank_mapping() 