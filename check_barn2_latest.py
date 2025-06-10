#!/usr/bin/env python3

import sys
import os

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes

def check_barn2_latest():
    """Check the latest T&K Barn 2 submission"""
    print("=== CHECKING T&K BARN 2 LATEST SUBMISSION ===\n")
    
    submissions = get_volume_submissions(hours_back=24)
    print(f"Found {len(submissions)} total submissions\n")
    
    # Filter for T&K Barn 2
    barn2_submissions = []
    for submission in submissions:
        parsed = parse_submission_volumes(submission)
        if parsed.get('dairy') == 'T&K [Barn 2]':
            barn2_submissions.append({
                'parsed': parsed,
                'raw': submission
            })
    
    if not barn2_submissions:
        print("No T&K [Barn 2] submissions found!")
        return
    
    # Sort by timestamp (most recent first)
    barn2_submissions.sort(key=lambda x: x['parsed']['timestamp'], reverse=True)
    
    print(f"Found {len(barn2_submissions)} T&K [Barn 2] submissions\n")
    
    # Show the latest one in detail
    latest = barn2_submissions[0]
    parsed = latest['parsed']
    raw = latest['raw']
    
    print("=== LATEST T&K [BARN 2] SUBMISSION ===")
    print(f"Timestamp: {parsed['timestamp']}")
    print(f"Submission ID: {parsed['submission_id']}")
    print(f"Volumes: {parsed['volumes']}")
    print(f"Milking Into: '{parsed['milking_into']}'")
    print(f"Pulled From: '{parsed['pulled_from']}'")
    
    print("\n=== RAW MILKING FIELDS FROM LATEST SUBMISSION ===")
    fields = raw.get('fields', [])
    milking_fields = []
    
    for i, field in enumerate(fields):
        label = field.get('label', '').strip().lower()
        if 'milking' in label and 'into' in label:
            milking_fields.append((i+1, field))
    
    if milking_fields:
        for idx, field in milking_fields:
            print(f"Field {idx}: {field['label']}")
            print(f"  Type: {field['type']}")
            if 'multipleChoiceValue' in field:
                value = field['multipleChoiceValue'].get('value', 'NO VALUE')
                print(f"  Value: '{value}'")
            else:
                print(f"  Value: NO MULTIPLE CHOICE VALUE")
            print()
    else:
        print("No milking fields found!")
    
    print("\n=== ALL T&K [BARN 2] SUBMISSIONS (last 24h) ===")
    for i, sub in enumerate(barn2_submissions):
        p = sub['parsed']
        print(f"{i+1}. {p['timestamp']} - Milking: '{p['milking_into']}' - Volumes: {p['volumes']}")

if __name__ == "__main__":
    check_barn2_latest() 