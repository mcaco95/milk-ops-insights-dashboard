#!/usr/bin/env python3
"""
Tank Data Debug Script
Shows raw form data vs calculated values vs database values
"""

import sys
import os
import psycopg2
from datetime import datetime
import json

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status, DAIRY_CONFIG

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "dairy_operations"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def debug_tank_data():
    """Debug tank data flow"""
    print("=== TANK DATA DEBUG ===\n")
    
    # Get raw form submissions
    print("1. RAW FORM SUBMISSIONS (last 24h):")
    submissions = get_volume_submissions(hours_back=24)
    print(f"Found {len(submissions)} form submissions\n")
    
    # Show recent T&K submissions
    tk_submissions = [s for s in submissions if 'T&K' in s.get('dairy', '')]
    print(f"T&K submissions: {len(tk_submissions)}")
    
    for i, sub in enumerate(tk_submissions[-3:]):  # Last 3 submissions
        print(f"\nSubmission {i+1}:")
        print(f"  Time: {sub.get('created_at')}")
        print(f"  Dairy: {sub.get('dairy')}")
        print(f"  Raw volumes: {sub.get('volumes', {})}")
        
        # Parse this submission
        parsed = parse_submission_volumes(sub)
        if parsed.get('volumes'):
            print(f"  Parsed volumes: {parsed['volumes']}")
            print(f"  Milking into: {parsed.get('milking_into')}")
            print(f"  Pulled from: {parsed.get('pulled_from')}")
    
    print("\n" + "="*50)
    
    # Get calculated tank status
    print("\n2. CALCULATED TANK STATUS:")
    current_data = []
    for submission in submissions:
        parsed = parse_submission_volumes(submission)
        if parsed.get('dairy') and parsed.get('volumes'):
            current_data.append(parsed)
    
    tank_statuses = calculate_tank_status(current_data)
    
    for dairy_name, tanks in tank_statuses.items():
        if 'T&K' in dairy_name:
            print(f"\n{dairy_name}:")
            for tank_name, tank_info in tanks.items():
                print(f"  {tank_name}:")
                print(f"    Current Volume: {tank_info.get('current_volume')} lbs")
                print(f"    Status: {tank_info.get('status')}")
                print(f"    Milking Into: {tank_info.get('milking_into')}")
                print(f"    Pulled From: {tank_info.get('pulled_from')}")
                print(f"    Is Being Filled: {tank_info.get('is_being_filled')}")
                print(f"    Last Update: {tank_info.get('last_update')}")
    
    print("\n" + "="*50)
    
    # Get database values
    print("\n3. DATABASE VALUES:")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT dairy_id, barn_name, tank_name, current_volume_lbs, 
                       is_milking, last_updated, capacity_lbs
                FROM tanks_data 
                WHERE dairy_id = 'tk_farms' 
                ORDER BY barn_name, tank_name
            """)
            
            print("TK Farms tanks in database:")
            for row in cur.fetchall():
                dairy_id, barn_name, tank_name, volume, is_milking, updated, capacity = row
                print(f"  {barn_name} - {tank_name}:")
                print(f"    Volume: {volume} lbs")
                print(f"    Is Milking: {is_milking}")
                print(f"    Capacity: {capacity} lbs")
                print(f"    Last Updated: {updated}")
    
    print("\n" + "="*50)
    
    # Show mapping issues
    print("\n4. POTENTIAL ISSUES:")
    
    # Check if form data has milking info
    has_milking_data = False
    for sub in tk_submissions[-5:]:
        parsed = parse_submission_volumes(sub)
        if parsed.get('milking_into') or parsed.get('pulled_from'):
            has_milking_data = True
            break
    
    if not has_milking_data:
        print("⚠️  No milking/pulling info found in recent form submissions")
    
    # Check volume discrepancies
    print("\n5. VOLUME COMPARISON:")
    print("Database vs Calculated:")
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT tank_name, current_volume_lbs FROM tanks_data WHERE dairy_id = 'tk_farms'")
            db_volumes = {row[0]: row[1] for row in cur.fetchall()}
    
    tk_calculated = tank_statuses.get('T&K [Barn 1]', {})
    tk_calculated.update(tank_statuses.get('T&K [Barn 2]', {}))
    tk_calculated.update(tank_statuses.get('T&K [Barn 3]', {}))
    
    for tank_name in set(list(db_volumes.keys()) + list(tk_calculated.keys())):
        db_vol = db_volumes.get(tank_name, 'Not in DB')
        calc_vol = tk_calculated.get(tank_name, {}).get('current_volume', 'Not calculated')
        
        if db_vol != calc_vol:
            print(f"  {tank_name}: DB={db_vol}, Calculated={calc_vol}")

if __name__ == "__main__":
    debug_tank_data() 