import requests
import os
import json
import re
from datetime import datetime, timedelta, timezone

# --- Configuration ---
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

def get_auth_headers():
    """Returns the authorization headers for the Samsara API request."""
    return {
        "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
        "Accept": "application/json"
    }

def extract_lt_number_from_route_name(route_name):
    """Extract LT/invoice number from Samsara route name."""
    # Pattern: "Route 75: CTD93137 Dickman (815)-Safeway-Tank 1"
    # Look for alphanumeric code after route number
    match = re.search(r'Route\s+\d+:\s+([A-Z]{3}\d{5})', route_name)
    if match:
        return match.group(1)
    return None

def find_dairy_stop(stops):
    """Find the dairy stop (middle stop, not processor)."""
    if len(stops) < 2:
        return None
    
    # Usually the dairy is the second stop (after start location, before processor)
    for i, stop in enumerate(stops):
        # Skip first and last stops (usually processors)
        if i > 0 and i < len(stops) - 1:
            return stop
    
    # Fallback: look for stops that aren't common processors
    processors = ['UDA', 'Safeway', 'Shamrock', 'Kroger', 'Fairlife', 'Schreiber']
    for stop in stops:
        stop_name = stop.get('name', '')
        if not any(proc in stop_name for proc in processors):
            return stop
    
    return None

def analyze_samsara_routes():
    """
    Fetches multiple routes from Samsara and analyzes them for dairy tracking.
    """
    print("=== SAMSARA ROUTES ANALYSIS ===")
    print("Fetching routes to analyze dairy tracking potential...\n")
    
    url = "https://api.samsara.com/fleet/routes"
    
    # Get routes from last 7 days
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=7)
    params = {
        "startTime": start_time.isoformat(),
        "endTime": end_time.isoformat(),
        "limit": 50  # Get more routes to analyze
    }
    
    try:
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        routes = response.json().get('data', [])
        
        if not routes:
            print("❌ No routes found in your Samsara account for the past 7 days.")
            return

        print(f"✅ Found {len(routes)} routes. Analyzing...\n")
        
        # Analyze each route
        dairy_routes = []
        
        for i, route in enumerate(routes[:10]):  # Analyze first 10 routes
            route_name = route.get('name', '')
            stops = route.get('stops', [])
            
            print(f"📍 Route {i+1}: {route_name}")
            
            # Extract LT number
            lt_number = extract_lt_number_from_route_name(route_name)
            print(f"   LT Number: {lt_number or 'Not found'}")
            
            # Find dairy stop
            dairy_stop = find_dairy_stop(stops)
            if dairy_stop:
                dairy_name = dairy_stop.get('name', 'Unknown')
                dairy_state = dairy_stop.get('state', 'unknown')
                dairy_arrival = dairy_stop.get('actualArrivalTime') or dairy_stop.get('scheduledArrivalTime')
                dairy_departure = dairy_stop.get('actualDepartureTime') or dairy_stop.get('scheduledDepartureTime')
                
                print(f"   🥛 Dairy: {dairy_name}")
                print(f"   📊 Status: {dairy_state}")
                print(f"   🕐 Arrival: {dairy_arrival}")
                print(f"   🕐 Departure: {dairy_departure}")
                
                # Determine tracking status
                if dairy_state == 'departed':
                    tracking_status = "✅ Completed"
                elif dairy_state == 'arrived':
                    tracking_status = "🟡 At Dairy"
                elif dairy_state in ['enRoute', 'dispatched']:
                    tracking_status = "🚛 En Route"
                else:
                    tracking_status = f"❓ {dairy_state}"
                
                print(f"   🎯 Tracking Status: {tracking_status}")
                
                dairy_routes.append({
                    'lt_number': lt_number,
                    'dairy_name': dairy_name,
                    'state': dairy_state,
                    'tracking_status': tracking_status,
                    'route_name': route_name
                })
            else:
                print(f"   ❌ No dairy stop found")
            
            print()
        
        # Summary
        print("=" * 60)
        print("📊 ANALYSIS SUMMARY")
        print("=" * 60)
        
        if dairy_routes:
            print(f"✅ Found {len(dairy_routes)} routes with dairy stops")
            print("\n🎯 Trackable Routes:")
            for route in dairy_routes:
                if route['lt_number']:
                    print(f"   LT: {route['lt_number']} | {route['dairy_name']} | {route['tracking_status']}")
            
            # Check for LT numbers that could match Milk Movement
            lt_numbers = [r['lt_number'] for r in dairy_routes if r['lt_number']]
            print(f"\n🔗 LT Numbers for Milk Movement matching: {lt_numbers}")
            
        else:
            print("❌ No dairy routes found for tracking")
            
        print("\n💡 INTEGRATION PLAN:")
        print("1. Fetch Samsara routes daily")
        print("2. Extract LT numbers from route names")  
        print("3. Match LT numbers with Milk Movement data")
        print("4. Track dairy stop status for real-time updates")
        print("5. Update route status: En Route → At Dairy → Completed")

    except requests.exceptions.RequestException as e:
        print(f"❌ FATAL: Could not get routes from Samsara: {e}")
        if hasattr(e, 'response') and e.response:
            print(f"Response Text: {e.response.text}")

if __name__ == "__main__":
    analyze_samsara_routes() 