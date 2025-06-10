#!/usr/bin/env python3
"""
Analyze the difference between routes and individual pickups 
from the Milk Movement raw data
"""

import json
from collections import defaultdict, Counter

def analyze_routes_vs_pickups():
    """Analyze the raw data to understand routes vs individual pickups."""
    
    # Load the raw data file
    try:
        with open('milk_movement_raw_2025-06-07_to_2025-06-10.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ Raw data file not found. Run test_milk_movement_raw.py first.")
        return
    
    print("🚛 ROUTES vs PICKUPS ANALYSIS")
    print("=" * 50)
    
    # Filter to just today's data (2025-06-09) AND hauler 77
    today_data = []
    for record in data:
        pickup_date = record.get('pickup_date', '')
        hauler_number = str(record.get('hauler_number', ''))
        
        if pickup_date.startswith('2025-06-09') and hauler_number == '77':
            today_data.append(record)
    
    print(f"📅 Records for today (2025-06-09) - HAULER 77 ONLY: {len(today_data)}")
    
    # Show all haulers for comparison
    all_today = [r for r in data if r.get('pickup_date', '').startswith('2025-06-09')]
    hauler_counts = Counter()
    for record in all_today:
        hauler_num = str(record.get('hauler_number', 'Unknown'))
        hauler_counts[hauler_num] += 1
    
    print(f"📊 ALL HAULERS TODAY: {len(all_today)} total records")
    print("   Top haulers:")
    for hauler, count in hauler_counts.most_common(5):
        marker = " ← YOU" if hauler == "77" else ""
        print(f"     Hauler {hauler}: {count} pickups{marker}")
    print()
    
    # Group by truck/route
    routes = defaultdict(list)
    
    for record in today_data:
        truck_num = record.get('truck_number', 'Unknown')
        route_num = record.get('route_number', 'Unknown')
        
        # Use truck_number as the route identifier
        route_key = f"Truck {truck_num}"
        if route_num != 'Unknown':
            route_key = f"Route {route_num} (Truck {truck_num})"
            
        routes[route_key].append(record)
    
    print(f"🚛 UNIQUE ROUTES (trucks): {len(routes)}")
    print(f"📦 TOTAL PICKUPS: {len(today_data)}")
    if len(routes) > 0:
        print(f"📊 AVERAGE PICKUPS PER ROUTE: {len(today_data) / len(routes):.1f}")
    print("\n" + "=" * 50)
    
    if len(routes) == 0:
        print("❌ NO ROUTES FOUND FOR HAULER 77 TODAY!")
        print("   This might explain why you're not seeing scheduled routes.")
        return
    
    # Show detailed breakdown
    print("📋 ROUTE BREAKDOWN:")
    print("-" * 50)
    
    routes_sorted = sorted(routes.items(), key=lambda x: len(x[1]), reverse=True)
    
    for route_key, pickups in routes_sorted[:15]:  # Show top 15 routes
        dairy_count = len(set(p.get('producer_name', 'Unknown') for p in pickups))
        tank_count = len(pickups)
        
        print(f"{route_key}:")
        print(f"  📦 {tank_count} pickups from {dairy_count} dairies")
        
        # Show which dairies
        dairy_pickups = defaultdict(list)
        for pickup in pickups:
            dairy = pickup.get('producer_name', 'Unknown')
            tank = pickup.get('producer_tank', 'Unknown')
            dairy_pickups[dairy].append(tank)
        
        for dairy, tanks in dairy_pickups.items():
            tanks_str = ', '.join(map(str, sorted(tanks)))
            print(f"    - {dairy}: tanks {tanks_str}")
        print()
    
    if len(routes_sorted) > 15:
        print(f"... and {len(routes_sorted) - 15} more routes")
    
    print("\n" + "=" * 50)
    print("🏭 DAIRY PICKUP SUMMARY:")
    print("-" * 50)
    
    # Count pickups by dairy
    dairy_counts = Counter()
    for record in today_data:
        dairy = record.get('producer_name', 'Unknown')
        dairy_counts[dairy] += 1
    
    for dairy, count in dairy_counts.most_common(10):
        print(f"{dairy}: {count} pickups")
    
    print("\n" + "=" * 50)
    print("💡 EXPLANATION:")
    print("-" * 50)
    print("• Each ROUTE = 1 truck doing its daily run")
    print("• Each PICKUP = 1 individual tank at 1 dairy")
    print("• Most trucks visit multiple dairies")
    print("• Many dairies have multiple tanks")
    print(f"• Hauler 77 has {len(routes)} routes with {len(today_data)} total pickups")

if __name__ == "__main__":
    analyze_routes_vs_pickups() 