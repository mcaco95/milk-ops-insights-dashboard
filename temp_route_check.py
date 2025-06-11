#!/usr/bin/env python3
import sys
sys.path.append('/app')
from get_daily_routes import get_samsara_routes_data
import json

print('=== FETCHING RAW SAMSARA ROUTES DATA ===')
samsara_routes = get_samsara_routes_data()

print(f'Total Samsara routes found: {len(samsara_routes)}')

# Look for route 145 or BVW35134
route_145_data = None
for route in samsara_routes:
    route_name = route.get('name', '')
    if '145' in route_name or 'BVW35134' in route_name:
        print(f'\n*** FOUND ROUTE 145 MATCH ***')
        print(f'Route Name: {route_name}')
        print(f'Raw Samsara Data:')
        print(json.dumps(route, indent=2))
        route_145_data = route
        break

if route_145_data is None:
    print('\n*** NO EXACT MATCH - LOOKING FOR T&K ROUTES ***')
    for route in samsara_routes:
        route_name = route.get('name', '')
        if 'T&K' in route_name:
            print(f'\nT&K Route Found:')
            print(f'Route Name: {route_name}')
            print(f'Route ID: {route.get("id")}')
            print(f'Status: {route.get("routeStatus")}')
            
    print('\n*** SHOWING ALL ROUTES WITH LT# BVW35134 ***')
    for route in samsara_routes:
        route_name = route.get('name', '')
        if 'BVW35134' in route_name:
            print(f'\nBVW35134 Route Found:')
            print(f'Route Name: {route_name}')
            print(f'Raw Data:')
            print(json.dumps(route, indent=2)) 