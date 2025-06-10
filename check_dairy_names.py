#!/usr/bin/env python3
"""
Check what dairy names are in form submissions
"""

import sys
import os

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions

def check_dairy_names():
    """Check what dairy names exist in submissions"""
    print("=== CHECKING DAIRY NAMES ===\n")
    
    submissions = get_volume_submissions(hours_back=48)
    print(f"Found {len(submissions)} form submissions in last 48 hours\n")
    
    # Get all unique dairy names
    dairy_names = set()
    for sub in submissions:
        dairy = sub.get('dairy', 'Unknown')
        dairy_names.add(dairy)
    
    print("All dairy names found:")
    for name in sorted(dairy_names):
        count = len([s for s in submissions if s.get('dairy') == name])
        print(f"  '{name}': {count} submissions")
    
    print("\n" + "="*50)
    
    # Show recent submissions with dairy names
    print("\nRecent 10 submissions:")
    for i, sub in enumerate(submissions[-10:]):
        print(f"{i+1}. {sub.get('created_at')} - '{sub.get('dairy')}' - Volumes: {len(sub.get('volumes', {}))}")

if __name__ == "__main__":
    check_dairy_names() 