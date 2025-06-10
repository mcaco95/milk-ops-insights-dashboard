#!/usr/bin/env python3
"""
Debug the parsing logic to see why dairy names and volumes are coming back as None
"""

import sys
import os

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes

def debug_parsing():
    """Debug the parsing logic"""
    print("=== DEBUGGING PARSING LOGIC ===\n")
    
    submissions = get_volume_submissions(hours_back=24)
    print(f"Found {len(submissions)} submissions\n")
    
    if not submissions:
        print("No submissions to analyze")
        return
    
    # Look at the first submission in detail
    first = submissions[0]
    print("=== FIRST SUBMISSION ANALYSIS ===")
    print(f"ID: {first.get('id')}")
    print(f"Submitted: {first.get('submittedAtTime')}")
    print(f"Status: {first.get('status')}")
    
    fields = first.get('fields', [])
    print(f"\nTotal fields: {len(fields)}")
    
    # Look for dairy field specifically
    dairy_fields = []
    volume_fields = []
    milking_fields = []
    
    print(f"\n=== FIELD ANALYSIS ===")
    for i, field in enumerate(fields):
        label = field.get('label', '').strip()
        field_type = field.get('type')
        field_id = field.get('id')
        
        print(f"{i+1:2d}. {label[:50]:50} ({field_type})")
        
        # Check dairy fields
        if 'dairy' in label.lower():
            dairy_fields.append(field)
            print(f"    ^^^ DAIRY FIELD - Full field: {field}")
        
        # Check volume fields  
        if 'volume' in label.lower() and field_type == 'number':
            volume_fields.append(field)
            if 'numberValue' in field:
                value = field['numberValue'].get('value')
                print(f"    ^^^ VOLUME FIELD - Value: {value}")
        
        # Check milking fields
        if 'milking' in label.lower():
            milking_fields.append(field)
            print(f"    ^^^ MILKING FIELD - Full field: {field}")
    
    print(f"\n=== SUMMARY ===")
    print(f"Dairy fields found: {len(dairy_fields)}")
    print(f"Volume fields found: {len(volume_fields)}")
    print(f"Milking fields found: {len(milking_fields)}")
    
    # Now test the parsing function
    print(f"\n=== TESTING PARSE FUNCTION ===")
    parsed = parse_submission_volumes(first)
    print(f"Parsed result: {parsed}")
    
    # Test parsing on a few more submissions
    print(f"\n=== TESTING MULTIPLE SUBMISSIONS ===")
    for i, sub in enumerate(submissions[:5]):
        parsed = parse_submission_volumes(sub)
        print(f"Submission {i+1}: dairy='{parsed.get('dairy')}', volumes={len(parsed.get('volumes', {}))}")

if __name__ == "__main__":
    debug_parsing() 