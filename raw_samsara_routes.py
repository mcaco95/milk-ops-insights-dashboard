#!/usr/bin/env python3
import requests
import json
from datetime import datetime, timezone

# Samsara API configuration
SAMSARA_TOKEN = 'samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE'
headers = {'Authorization': f'Bearer {SAMSARA_TOKEN}'}

print('=== RAW SAMSARA ROUTES API DATA ===')

# Get today's date range in RFC 3339 format
today = datetime.now(timezone.utc)
start_time = today.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
end_time = today.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

print(f'Fetching routes from {start_time} to {end_time}')

# Get all routes from Samsara with required time parameters
routes_url = 'https://api.samsara.com/fleet/routes'
params = {
    'startTime': start_time,
    'endTime': end_time,
    'limit': 512
}

response = requests.get(routes_url, headers=headers, params=params)
routes_data = response.json()

print(f'Total routes returned: {len(routes_data.get("data", []))}')
print(f'Full API Response:')
print(json.dumps(routes_data, indent=2))

print('\n=== LOOKING FOR ROUTE 145 ===')
for i, route in enumerate(routes_data.get('data', [])):
    route_name = route.get('name', '')
    if '145' in route_name:
        print(f'\n*** FOUND ROUTE 145 ***')
        print(f'Index: {i}')
        print(f'Route Name: {route_name}')
        print(f'Full Route Data:')
        print(json.dumps(route, indent=2)) 