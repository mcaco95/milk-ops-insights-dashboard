#!/usr/bin/env python3
"""
Debug script to check parsing for all dairies
"""

import sys
import os
from collections import defaultdict

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, DAIRY_CONFIG

def debug_all_dairies():
    """Debug parsing for all configured dairies"""
    print("=== DEBUGGING ALL DAIRIES ===\n")
    
    # Get recent submissions
    print("Fetching form submissions from last 48 hours...")
    submissions = get_volume_submissions(hours_back=48)
    print(f"Found {len(submissions)} total submissions\n")
    
    # Track data by dairy
    dairy_data = defaultdict(list)
    parsing_issues = []
    
    # Parse all submissions
    for i, submission in enumerate(submissions):
        parsed = parse_submission_volumes(submission)
        dairy_name = parsed.get('dairy')
        
        if dairy_name:
            dairy_data[dairy_name].append(parsed)
        else:
            parsing_issues.append({
                'submission_id': submission.get('id'),
                'index': i,
                'fields': [f.get('label', 'NO_LABEL') for f in submission.get('fields', [])]
            })
    
    # Report configured vs found dairies
    print("=== CONFIGURED DAIRIES ===")
    configured_dairies = set(DAIRY_CONFIG.keys())
    for dairy in sorted(configured_dairies):
        print(f"✓ {dairy}")
    
    print(f"\n=== FOUND IN SUBMISSIONS ({len(dairy_data)} dairies) ===")
    found_dairies = set(dairy_data.keys())
    for dairy in sorted(found_dairies):
        count = len(dairy_data[dairy])
        print(f"✓ {dairy} ({count} submissions)")
    
    # Check for mismatches
    missing_from_submissions = configured_dairies - found_dairies
    not_in_config = found_dairies - configured_dairies
    
    if missing_from_submissions:
        print(f"\n❌ DAIRIES IN CONFIG BUT NO SUBMISSIONS:")
        for dairy in sorted(missing_from_submissions):
            print(f"   - {dairy}")
    
    if not_in_config:
        print(f"\n⚠️  DAIRIES IN SUBMISSIONS BUT NOT IN CONFIG:")
        for dairy in sorted(not_in_config):
            print(f"   - {dairy}")
    
    # Check volume data quality
    print(f"\n=== VOLUME DATA ANALYSIS ===")
    for dairy_name in sorted(found_dairies):
        submissions = dairy_data[dairy_name]
        latest = max(submissions, key=lambda x: x.get('timestamp', ''))
        
        volume_count = len(latest.get('volumes', {}))
        expected_tanks = len(DAIRY_CONFIG.get(dairy_name, {}).get('tanks', {}))
        milking_status = latest.get('milking_into', 'None')
        
        status = "✓" if volume_count > 0 else "❌"
        print(f"{status} {dairy_name}:")
        print(f"   Volumes: {volume_count}/{expected_tanks} tanks")
        print(f"   Milking: {milking_status}")
        print(f"   Latest: {latest.get('timestamp', 'N/A')}")
        
        if volume_count == 0:
            print(f"   🔍 Tank names in latest submission: {list(latest.get('volumes', {}).keys())}")
    
    # Show parsing issues
    if parsing_issues:
        print(f"\n❌ PARSING ISSUES ({len(parsing_issues)} submissions):")
        for issue in parsing_issues[:5]:  # Show first 5
            print(f"   Submission {issue['index']}: {issue['fields'][:3]}...")
    
    print(f"\n=== SUMMARY ===")
    print(f"Configured dairies: {len(configured_dairies)}")
    print(f"Found in submissions: {len(found_dairies)}")
    print(f"Parsing issues: {len(parsing_issues)}")
    print(f"Missing data: {len([d for d in found_dairies if len(dairy_data[d][-1].get('volumes', {})) == 0])}")

if __name__ == "__main__":
    debug_all_dairies() 