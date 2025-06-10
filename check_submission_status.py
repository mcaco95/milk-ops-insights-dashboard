#!/usr/bin/env python3

import sys
import os

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes

def check_submission_status():
    """Check submission status for all T&K barns"""
    print("=== CHECKING SUBMISSION STATUS ===\n")
    
    submissions = get_volume_submissions(hours_back=48)
    
    # Group by dairy
    by_dairy = {}
    
    for submission in submissions:
        parsed = parse_submission_volumes(submission)
        dairy = parsed.get('dairy')
        
        if dairy and 'T&K' in dairy:
            if dairy not in by_dairy:
                by_dairy[dairy] = []
            
            by_dairy[dairy].append({
                'timestamp': parsed['timestamp'],
                'status': submission.get('status', 'unknown'),
                'milking_into': parsed['milking_into'],
                'volumes': parsed['volumes'],
                'submission_id': submission.get('id', 'unknown')
            })
    
    # Sort each dairy by timestamp
    for dairy in by_dairy:
        by_dairy[dairy].sort(key=lambda x: x['timestamp'], reverse=True)
    
    # Print results
    for dairy, subs in by_dairy.items():
        print(f"=== {dairy} ===")
        print(f"Total submissions: {len(subs)}")
        
        for i, sub in enumerate(subs[:3]):  # Show top 3
            print(f"  {i+1}. {sub['timestamp']}")
            print(f"     Status: {sub['status']}")
            print(f"     Milking: '{sub['milking_into']}'")
            print(f"     Volumes: {sub['volumes']}")
            print(f"     ID: {sub['submission_id']}")
        
        if len(subs) > 3:
            print(f"     ... and {len(subs) - 3} more")
        print()

if __name__ == "__main__":
    check_submission_status() 