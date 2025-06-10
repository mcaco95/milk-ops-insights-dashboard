import sys
sys.path.append('/app')
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, DAIRY_CONFIG
from collections import defaultdict

print("=== DEBUGGING ALL DAIRIES ===")
submissions = get_volume_submissions(hours_back=48)
print(f"Found {len(submissions)} submissions")

dairy_data = defaultdict(list)
for submission in submissions:
    parsed = parse_submission_volumes(submission)
    dairy_name = parsed.get('dairy')
    if dairy_name:
        dairy_data[dairy_name].append(parsed)

print(f"Configured: {len(DAIRY_CONFIG)}, Found: {len(dairy_data)}")

print("\n=== DAIRY STATUS ===")
for dairy, subs in sorted(dairy_data.items()):
    latest = max(subs, key=lambda x: x.get('timestamp', ''))
    vol_count = len(latest.get('volumes', {}))
    expected = len(DAIRY_CONFIG.get(dairy, {}).get('tanks', {}))
    milking = latest.get('milking_into', 'None')
    print(f"{dairy}: {len(subs)} subs, {vol_count}/{expected} vols, milking: {milking}")

missing = set(DAIRY_CONFIG.keys()) - set(dairy_data.keys())
if missing:
    print(f"\n❌ MISSING DAIRIES: {sorted(missing)}")
else:
    print(f"\n✓ All dairies found!") 