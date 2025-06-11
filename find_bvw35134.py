#!/usr/bin/env python3
import requests
import json

# Samsara API configuration
SAMSARA_TOKEN = 'samsara_api_81c1df44-efb6-4252-b18e-8a40fffce5c5'
headers = {'Authorization': f'Bearer {SAMSARA_TOKEN}'}

print('=== FETCHING SAMSARA ROUTES FOR BVW35134 ===')

routes_url = 'https://api.samsara.com/fleet/routes'
response = requests.get(routes_url, headers=headers, params={'limit': 100})
routes_data = response.json()

print(f'Found {len(routes_data.get("data", []))} total routes')

# Look for BVW35134 specifically
bvw_found = False
for route in routes_data.get('data', []):
    route_name = route.get('name', '')
    if 'BVW35134' in route_name:
        print(f'\n*** FOUND LT# BVW35134 ROUTE ***')
        print(f'Route Name: {route_name}')
        print(f'Route ID: {route.get("id")}')
        print(f'Route Status: {route.get("routeStatus")}')
        print(f'Start Time: {route.get("routeStartingTime")}')
        print(f'Actual Start Time: {route.get("actualRouteStartTime")}')
        print(f'Completion Time: {route.get("routeCompletionTime")}')
        print('\nFull Raw Data:')
        print(json.dumps(route, indent=2))
        bvw_found = True
        break

if not bvw_found:
    print('\nBVW35134 not found directly. Checking for similar patterns...')
    for route in routes_data.get('data', []):
        route_name = route.get('name', '')
        if 'BVW' in route_name or '145' in route_name:
            print(f'Similar pattern: {route_name} (ID: {route.get("id")})') 