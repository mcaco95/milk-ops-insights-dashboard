#!/usr/bin/env python3
"""
DATA FLOW DEBUG SCRIPT WITH DETAILED LOGGING
Traces: Raw API → Tank Extraction → Database Storage
Includes timezone fix for Samsara API
"""

import requests
import re
import psycopg2
import pytz
from datetime import datetime, timezone, timedelta
import json

# API credentials
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

# Database config
DB_CONFIG = {
    "host": "localhost",
    "port": "5432", 
    "database": "dairy_operations",
    "user": "postgres",
    "password": "31012662"
}

def get_samsara_routes_with_logging():
    """Get Samsara routes with detailed tank extraction logging"""
    print("\n🚛 SAMSARA API - DETAILED LOGGING")
    print("=" * 60)
    
    # FIXED TIMEZONE LOGIC
    mst = pytz.timezone('America/Phoenix')
    mst_now = datetime.now(mst)
    
    # Get MST business day, then convert to UTC for API
    mst_today = mst_now.replace(hour=0, minute=0, second=0, microsecond=0)
    mst_tomorrow = mst_today + timedelta(days=1)
    
    start_utc = mst_today.astimezone(timezone.utc)
    end_utc = mst_tomorrow.astimezone(timezone.utc)
    
    print(f"🕐 FIXED TIMEZONE LOGIC:")
    print(f"   MST Business Day: {mst_today.strftime('%Y-%m-%d %H:%M')} to {mst_tomorrow.strftime('%Y-%m-%d %H:%M')}")
    print(f"   UTC API Range: {start_utc.isoformat()} to {end_utc.isoformat()}")
    print()
    
    url = "https://api.samsara.com/fleet/routes"
    headers = {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}
    params = {
        "startTime": start_utc.isoformat(),
        "endTime": end_utc.isoformat(),
        "limit": 500
    }
    
    print(f"📡 API Call: {url}")
    print(f"📡 Params: {json.dumps(params, indent=2)}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        routes = data.get('data', [])
        print(f"✅ API Response: {len(routes)} total routes")
        print()
        
        # Process routes and log tank extraction
        tank_extraction_examples = []
        status_examples = []
        
        for i, route in enumerate(routes[:10]):  # First 10 for detailed logging
            route_name = route.get('name', '')
            
            # Extract LT number
            lt_match = re.search(r'([A-Z]{3}\d{5})', route_name)
            lt_number = lt_match.group(1) if lt_match else 'NO_LT'
            
            # Extract tank number - DETAILED LOGGING
            tank_match = re.search(r'[Tt]ank\s*(\d+)', route_name)
            samsara_tank = tank_match.group(1) if tank_match else None
            
            if tank_match:
                tank_extraction_examples.append({
                    'route_name': route_name,
                    'lt_number': lt_number,
                    'tank_extracted': samsara_tank,
                    'raw_match': tank_match.group(0)
                })
            
            # Analyze stops for status
            stops = route.get('stops', [])
            dairy_stop = None
            depot_stop = None
            
            for j, stop in enumerate(stops):
                stop_name = stop.get('name', '').lower()
                
                if j == 0 or (stop.get('scheduledDepartureTime') and not stop.get('scheduledArrivalTime')):
                    depot_stop = stop
                elif (stop.get('scheduledArrivalTime') and stop.get('scheduledDepartureTime') and 
                      any(word in stop_name for word in ['dairy', 'holsteins', 't&k', 'dickman', 'milky', 'triple'])):
                    if dairy_stop is None:
                        dairy_stop = stop
            
            # Determine status
            status = "scheduled"
            dairy_state = ""
            depot_state = ""
            
            if dairy_stop:
                dairy_state = dairy_stop.get('state', '')
                if dairy_state == 'departed':
                    status = "completed"
                elif dairy_state == 'arrived':
                    status = "filling_tank"
                elif dairy_state == 'skipped':
                    if depot_stop and depot_stop.get('state') == 'departed':
                        status = "en_route"
                        
            if depot_stop:
                depot_state = depot_stop.get('state', '')
            
            # Log status examples
            if status != 'scheduled' and len(status_examples) < 3:
                status_examples.append({
                    'lt_number': lt_number,
                    'route_name': route_name,
                    'status': status,
                    'dairy_state': dairy_state,
                    'depot_state': depot_state,
                    'dairy_stop': dairy_stop.get('name', '') if dairy_stop else '',
                    'times': {
                        'dairy_arrival': dairy_stop.get('actualArrivalTime', '') if dairy_stop else '',
                        'dairy_departure': dairy_stop.get('actualDepartureTime', '') if dairy_stop else '',
                        'depot_departure': depot_stop.get('actualDepartureTime', '') if depot_stop else ''
                    }
                })
        
        # Display tank extraction examples
        print("🏷️  TANK EXTRACTION EXAMPLES:")
        if tank_extraction_examples:
            for example in tank_extraction_examples[:3]:
                print(f"   📝 Route: {example['route_name']}")
                print(f"      LT: {example['lt_number']}")
                print(f"      Tank Found: '{example['raw_match']}' → Extracted: {example['tank_extracted']}")
                print()
        else:
            print("   ❌ No tank information found in route names")
            print()
        
        # Display status examples  
        print("📊 STATUS DETERMINATION EXAMPLES:")
        if status_examples:
            for example in status_examples:
                print(f"   🚛 {example['lt_number']} ({example['route_name'][:50]}...)")
                print(f"      Status: {example['status']}")
                print(f"      Dairy Stop: {example['dairy_stop']} (State: {example['dairy_state']})")
                print(f"      Depot State: {example['depot_state']}")
                if example['times']['dairy_arrival']:
                    arrival_time = datetime.fromisoformat(example['times']['dairy_arrival'].replace('Z', '+00:00'))
                    arrival_mst = arrival_time.astimezone(mst).strftime('%H:%M MST')
                    print(f"      Dairy Arrival: {arrival_mst}")
                if example['times']['dairy_departure']:
                    departure_time = datetime.fromisoformat(example['times']['dairy_departure'].replace('Z', '+00:00'))
                    departure_mst = departure_time.astimezone(mst).strftime('%H:%M MST')
                    print(f"      Dairy Departure: {departure_mst}")
                print()
        else:
            print("   ℹ️  All routes are 'scheduled' (no active/completed routes found)")
            print()
        
        print(f"📈 SUMMARY:")
        print(f"   Total Routes: {len(routes)}")
        print(f"   Tank Info Found: {len(tank_extraction_examples)}")
        print(f"   Active/Completed: {len(status_examples)}")
        
        return routes, tank_extraction_examples, status_examples
        
    except Exception as e:
        print(f"❌ Samsara API Error: {e}")
        return [], [], []

def check_database_storage():
    """Check what's actually stored in the database"""
    print("\n💾 DATABASE STORAGE CHECK")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Check total routes today
        cur.execute("SELECT COUNT(*) FROM routes_data WHERE report_date = CURRENT_DATE")
        total_routes = cur.fetchone()[0]
        
        # Check routes with tank info
        cur.execute("""
            SELECT COUNT(*) FROM routes_data 
            WHERE report_date = CURRENT_DATE AND samsara_tank IS NOT NULL
        """)
        routes_with_tanks = cur.fetchone()[0]
        
        # Get examples of tank data
        cur.execute("""
            SELECT lt_number, dairy_name, tank, samsara_tank, status 
            FROM routes_data 
            WHERE report_date = CURRENT_DATE AND samsara_tank IS NOT NULL 
            ORDER BY samsara_tank 
            LIMIT 5
        """)
        tank_examples = cur.fetchall()
        
        # Get status distribution
        cur.execute("""
            SELECT status, COUNT(*) 
            FROM routes_data 
            WHERE report_date = CURRENT_DATE 
            GROUP BY status 
            ORDER BY status
        """)
        status_dist = cur.fetchall()
        
        print(f"📊 DATABASE CONTENTS:")
        print(f"   Total Routes Today: {total_routes}")
        print(f"   Routes with Tank Info: {routes_with_tanks}")
        print()
        
        print(f"📈 STATUS DISTRIBUTION:")
        for status, count in status_dist:
            print(f"   {status}: {count}")
        print()
        
        print(f"🏷️  TANK DATA EXAMPLES:")
        if tank_examples:
            for lt_number, dairy_name, tank, samsara_tank, status in tank_examples:
                print(f"   {lt_number}: {dairy_name[:20]}")
                print(f"      MM Tank: {tank or 'None'}")
                print(f"      Samsara Tank: {samsara_tank}")
                print(f"      Status: {status}")
                print()
        else:
            print("   ❌ No routes with tank information in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database Error: {e}")

def main():
    """Run the complete data flow debug"""
    print("🔍 DATA FLOW DEBUG WITH LOGGING")
    print("Tracing: Raw API → Tank Extraction → Database Storage")
    print("=" * 80)
    
    # Step 1: Get raw data from Samsara with logging
    routes, tank_examples, status_examples = get_samsara_routes_with_logging()
    
    # Step 2: Check what's in database
    check_database_storage()
    
    # Step 3: Comparison and recommendations
    print("\n🎯 FINDINGS & RECOMMENDATIONS:")
    print("=" * 60)
    
    if tank_examples:
        print("✅ Tank extraction is working from Samsara route names")
        print("   → Check if populate script stores these in database correctly")
    else:
        print("❌ No tank info found in current Samsara routes")
        print("   → May be due to timezone issue or route naming changes")
    
    if status_examples:
        print("✅ Status determination is working for active routes")
        print("   → Check if status mapping stores correctly in database")
    else:
        print("⚠️  All routes are 'scheduled' - no active routes at this time")
        print("   → Normal if outside business hours")
    
    print("\n💡 NEXT STEPS:")
    print("1. Fix timezone issue in populate_routes_data.py")
    print("2. Add samsara_tank to backend API response")
    print("3. Update frontend to use samsara_tank priority")
    print("4. Fix timestamp logic for filling_tank vs completed status")

if __name__ == "__main__":
    main() 