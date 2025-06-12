#!/usr/bin/env python3
"""
Debug Mapping Issue Script

This script tests the exact mapping function from populate_tanks_data.py
and compares it with actual form submissions to find the mismatch.
"""

import sys
import os
import psycopg2

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tank_level_dashboard import get_volume_submissions, parse_submission_volumes
from scripts.populate_tanks_data import get_db_connection, get_dairy_mapping

def debug_mapping_issue():
    """Debug the exact mapping issue."""
    print("🔍 DEBUGGING MAPPING ISSUE")
    print("=" * 60)
    
    # The three troubled dairies
    troubled_dairies = ["Arizona Dairy", "D&I Coolidge (805)", "D&I Stanfield (716)"]
    
    try:
        # Step 1: Test the database mapping function
        print("\n1. TESTING DATABASE MAPPING FUNCTION")
        print("-" * 40)
        
        with get_db_connection() as conn:
            dairy_mapping = get_dairy_mapping(conn)
            
            print(f"Total mappings found: {len(dairy_mapping)}")
            print("\nAll mappings:")
            for form_name, dairy_id in sorted(dairy_mapping.items()):
                print(f"  '{form_name}' -> {dairy_id}")
            
            print(f"\nChecking troubled dairies in mapping:")
            for dairy_name in troubled_dairies:
                if dairy_name in dairy_mapping:
                    print(f"  ✅ '{dairy_name}' -> {dairy_mapping[dairy_name]}")
                else:
                    print(f"  ❌ '{dairy_name}' -> NOT FOUND")
                    
                    # Check for similar names
                    print(f"     Similar names in mapping:")
                    for mapped_name in dairy_mapping.keys():
                        if any(word.lower() in mapped_name.lower() for word in dairy_name.split()):
                            print(f"       - '{mapped_name}'")
        
        # Step 2: Test form submissions
        print("\n\n2. TESTING FORM SUBMISSIONS")
        print("-" * 40)
        
        submissions = get_volume_submissions(hours_back=48)
        print(f"Total submissions: {len(submissions)}")
        
        form_dairy_names = set()
        troubled_submissions = {}
        
        for submission in submissions:
            parsed = parse_submission_volumes(submission)
            dairy_name = parsed.get('dairy')
            if dairy_name:
                form_dairy_names.add(dairy_name)
                if dairy_name in troubled_dairies:
                    if dairy_name not in troubled_submissions:
                        troubled_submissions[dairy_name] = []
                    troubled_submissions[dairy_name].append(parsed)
        
        print(f"\nUnique dairy names from forms:")
        for name in sorted(form_dairy_names):
            print(f"  '{name}'")
        
        print(f"\nTroubled dairy submissions:")
        for dairy_name in troubled_dairies:
            if dairy_name in troubled_submissions:
                subs = troubled_submissions[dairy_name]
                print(f"  ✅ '{dairy_name}': {len(subs)} submissions")
                if subs:
                    print(f"     Sample volumes: {subs[0].get('volumes', {})}")
            else:
                print(f"  ❌ '{dairy_name}': NO SUBMISSIONS")
        
        # Step 3: Character-by-character comparison
        print("\n\n3. CHARACTER-BY-CHARACTER COMPARISON")
        print("-" * 40)
        
        with get_db_connection() as conn:
            dairy_mapping = get_dairy_mapping(conn)
            
            for dairy_name in troubled_dairies:
                print(f"\nAnalyzing '{dairy_name}':")
                print(f"  Length: {len(dairy_name)}")
                print(f"  Bytes: {dairy_name.encode('utf-8')}")
                print(f"  Repr: {repr(dairy_name)}")
                
                # Check if it exists in mapping
                found_exact = dairy_name in dairy_mapping
                print(f"  Exact match in mapping: {found_exact}")
                
                if not found_exact:
                    print(f"  Checking for close matches:")
                    for mapped_name in dairy_mapping.keys():
                        if dairy_name.lower() == mapped_name.lower():
                            print(f"    Case difference: '{mapped_name}' vs '{dairy_name}'")
                        elif dairy_name.strip() == mapped_name.strip():
                            print(f"    Whitespace difference: '{mapped_name}' vs '{dairy_name}'")
                        elif len(dairy_name) == len(mapped_name):
                            diff_chars = []
                            for i, (c1, c2) in enumerate(zip(dairy_name, mapped_name)):
                                if c1 != c2:
                                    diff_chars.append(f"pos {i}: '{c1}' vs '{c2}'")
                            if diff_chars:
                                print(f"    Character differences with '{mapped_name}': {diff_chars}")
        
        # Step 4: Raw database array inspection
        print("\n\n4. RAW DATABASE ARRAY INSPECTION")
        print("-" * 40)
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, tank_dashboard_names 
                    FROM dairies 
                    WHERE id IN ('az_dairy', 'd_i_dairy', 'd_i_holsteins')
                    ORDER BY id
                """)
                
                for row in cur.fetchall():
                    dairy_id, names_array = row
                    print(f"\n{dairy_id}:")
                    print(f"  Raw array: {names_array}")
                    print(f"  Type: {type(names_array)}")
                    
                    if names_array:
                        print(f"  Array contents:")
                        for i, name in enumerate(names_array):
                            print(f"    [{i}] '{name}' (len={len(name)}, bytes={name.encode('utf-8')})")
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n✅ DEBUG COMPLETE")

if __name__ == "__main__":
    debug_mapping_issue() 