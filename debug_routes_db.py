#!/usr/bin/env python3
"""
Debug script to check what's in the routes database vs Samsara API
"""

import psycopg2
import json
from datetime import date, datetime
import requests
import os

# Database connection
DB_URL = "postgresql://postgres:password@localhost:5432/dairy_operations"
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

def get_db_routes():
    """Get T&K routes from database for today"""
    conn = psycopg2.connect(DB_URL)
    cur = conn.cursor()
    
    print("=== T&K ROUTES IN DATABASE FOR TODAY ===")
    cur.execute("""
        SELECT 
            route, dairy_name, tank, status, start_date, estimated_arrival, 
            driver_name, truck_id, processor, samsara_route_id, last_updated
        FROM routes_data 
        WHERE dairy_name LIKE '%T&K%' 
        AND report_date = %s
        ORDER BY start_date
    """, (date.today(),))
    
    routes = cur.fetchall()
    for i, route in enumerate(routes):
        print(f"{i+1:2d}. Route {route[0]} | Tank {route[2]} | Status: {route[3]} | Start: {route[4]} | Driver: {route[6]} | Updated: {route[10]}")
    
    print(f"\nTotal T&K routes in database: {len(routes)}")
    
    # Check specifically for Route 145
    cur.execute("""
        SELECT * FROM routes_data 
        WHERE route = '145' AND dairy_name LIKE '%T&K%' 
        AND report_date = %s
    """, (date.today(),))
    
    route_145 = cur.fetchone()
    if route_145:
        print(f"\n=== ROUTE 145 DATABASE DETAILS ===")
        print(f"Route: {route_145[2]}")
        print(f"Status: {route_145[5]}")
        print(f"Start Date: {route_145[4]}")
        print(f"Driver: {route_145[6]}")
        print(f"Truck: {route_145[7]}")
        print(f"Last Updated: {route_145[11]}")
    else:
        print(f"\n❌ Route 145 NOT FOUND in database!")
    
    conn.close()
    return routes, route_145

def get_samsara_route_145():
    """Get Route 145 from Samsara API"""
    print(f"\n=== SAMSARA ROUTE 145 STATUS ===")
    
    url = "https://api.samsara.com/fleet/routes"
    headers = {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}
    
    # Get today's routes
    today = datetime.now().strftime("%Y-%m-%d")
    start_time = f"{today}T00:00:00.000Z"
    end_time = f"{today}T23:59:59.999Z"
    
    params = {
        "startTime": start_time,
        "endTime": end_time,
        "limit": 100
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        routes = response.json().get('data', [])
        
        # Find Route 145
        route_145 = None
        for route in routes:
            if "Route 145:" in route.get('name', ''):
                route_145 = route
                break
        
        if route_145:
            print(f"✅ Found Route 145 in Samsara")
            print(f"Name: {route_145['name']}")
            print(f"Driver: {route_145.get('driver', {}).get('name', 'Unknown')}")
            print(f"Start Time: {route_145.get('actualRouteStartTime', 'N/A')}")
            print(f"End Time: {route_145.get('actualRouteEndTime', 'N/A')}")
            
            # Check T&K stop status
            stops = route_145.get('stops', [])
            for stop in stops:
                if 'T&K' in stop.get('name', ''):
                    print(f"T&K Stop Status: {stop.get('state')}")
                    print(f"T&K Arrival: {stop.get('actualArrivalTime', 'N/A')}")
                    print(f"T&K Departure: {stop.get('actualDepartureTime', 'N/A')}")
                    break
        else:
            print(f"❌ Route 145 NOT FOUND in Samsara")
            
        return route_145
        
    except Exception as e:
        print(f"❌ Error fetching from Samsara: {e}")
        return None

if __name__ == "__main__":
    print(f"🔍 Debugging Route 145 Status Mismatch - {datetime.now()}")
    
    # Check database
    db_routes, db_route_145 = get_db_routes()
    
    # Check Samsara
    samsara_route_145 = get_samsara_route_145()
    
    print(f"\n=== COMPARISON SUMMARY ===")
    if db_route_145 and samsara_route_145:
        print(f"Database Status: {db_route_145[5]}")
        print(f"Database Updated: {db_route_145[11]}")
        
        # Determine what Samsara status should be
        stops = samsara_route_145.get('stops', [])
        dairy_departed = False
        for stop in stops:
            if 'T&K' in stop.get('name', '') and stop.get('state') == 'departed':
                dairy_departed = True
                break
        
        samsara_status = "Completed" if dairy_departed else "Active"
        print(f"Samsara Status Should Be: {samsara_status}")
        
        if db_route_145[5] != samsara_status.lower():
            print(f"🚨 STATUS MISMATCH! Database is outdated.")
        else:
            print(f"✅ Status matches")
    else:
        print(f"❌ Cannot compare - missing data") 