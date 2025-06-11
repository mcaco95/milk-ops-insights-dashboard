#!/usr/bin/env python3
"""
Test timezone conversion for Route 145 departure time
"""

from datetime import datetime, timezone
import pytz

# Raw Samsara departure time for Route 145
samsara_time = "2025-06-10T14:07:40.059Z"

print(f"🔍 Testing timezone conversion for Route 145:")
print(f"Raw Samsara time: {samsara_time}")

# Parse the UTC time
utc_time = datetime.fromisoformat(samsara_time.replace('Z', '+00:00'))
print(f"Parsed UTC time: {utc_time}")

# Convert to MST (Arizona timezone)
mst = pytz.timezone('America/Phoenix')
mst_time = utc_time.astimezone(mst)
mst_formatted = mst_time.strftime('%H:%M MST')

print(f"MST time: {mst_time}")
print(f"Formatted MST: {mst_formatted}")

# Manual calculation check
print(f"\n🧮 Manual check:")
print(f"14:07 UTC - 7 hours = 07:07 MST")
print(f"Expected: 07:07 MST")
print(f"Got: {mst_formatted}")

if "07:07" in mst_formatted:
    print("✅ CORRECT!")
else:
    print("❌ WRONG! Timezone conversion has a bug!") 