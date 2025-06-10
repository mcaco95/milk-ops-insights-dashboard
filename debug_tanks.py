#!/usr/bin/env python3
import sys
sys.path.append('/app')
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status

print("Fetching submissions...")
submissions = get_volume_submissions(hours_back=48)
print(f"Found {len(submissions)} total submissions")

# Look for T&K submissions
tk_submissions = []
for s in submissions:
    parsed = parse_submission_volumes(s)
    if parsed and parsed.get('dairy') and 'T&K' in parsed.get('dairy'):
        tk_submissions.append(parsed)

print(f"\nFound {len(tk_submissions)} T&K submissions:")
for i, tk in enumerate(tk_submissions[:5]):
    print(f"  {i+1}. {tk['dairy']}: {tk['volumes']}")

# Check what calculate_tank_status returns
if tk_submissions:
    print(f"\nCalculating tank status from {len(tk_submissions)} T&K submissions...")
    tank_statuses = calculate_tank_status(tk_submissions)
    print("Tank statuses calculated:")
    for dairy_name, tanks in tank_statuses.items():
        if 'T&K' in dairy_name:
            print(f"  {dairy_name}:")
            for tank_name, tank_info in tanks.items():
                volume = tank_info.get('current_volume_lbs', 'N/A')
                print(f"    {tank_name}: {volume} lbs") 