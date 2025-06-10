#!/usr/bin/env python3
"""
Analyze all haulers in the schedules data to find hauler 77
"""

import requests
import json
from datetime import datetime, timedelta
from collections import Counter

# Configuration
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"

def get_auth_headers():
    """Returns the authorization headers for Milk Movement API."""
    return {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}

def analyze_schedule_haulers():
    """Analyze what haulers exist in the schedules data."""
    
    print("🔍 ANALYZING SCHEDULE HAULERS")
    print("=" * 50)
    
    # Get schedules data
    now = datetime.now()
    start_date = (now - timedelta(hours=24)).strftime("%Y-%m-%d")
    end_date = (now + timedelta(hours=48)).strftime("%Y-%m-%d")
    
    url = f"{API_BASE_URL}/schedules"
    params = {"start_date": start_date, "end_date": end_date}
    
    try:
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        
        data = response.json()
        print(f"📊 Total schedule records: {len(data)}")
        
        # Extract all hauler info
        haulers = Counter()
        hauler_details = {}
        
        for record in data:
            hauler_info = record.get('hauler', {})
            if hauler_info:
                hauler_num = hauler_info.get('hauler_number', 'Unknown')
                hauler_name = hauler_info.get('name', 'Unknown')
                hauler_id = hauler_info.get('_id', 'Unknown')
                
                haulers[hauler_num] += 1
                hauler_details[hauler_num] = {
                    'name': hauler_name,
                    'id': hauler_id
                }
        
        print(f"\n🚛 HAULERS FOUND IN SCHEDULES:")
        print("-" * 40)
        
        for hauler_num, count in haulers.most_common():
            details = hauler_details.get(hauler_num, {})
            name = details.get('name', 'Unknown')
            
            marker = " ← YOU?" if hauler_num == '77' else ""
            print(f"Hauler {hauler_num}: {count} schedules{marker}")
            print(f"  Name: {name}")
            print()
        
        # Check if 77 exists
        if '77' in haulers:
            print(f"✅ FOUND HAULER 77 in schedules!")
            hauler_77_count = haulers['77']
            
            # Show hauler 77 schedule details
            hauler_77_schedules = []
            for record in data:
                hauler_info = record.get('hauler', {})
                if hauler_info.get('hauler_number') == '77':
                    hauler_77_schedules.append(record)
            
            print(f"📦 Hauler 77 has {hauler_77_count} scheduled pickups")
            
            # Group by date
            from collections import defaultdict
            by_date = defaultdict(int)
            
            for schedule in hauler_77_schedules:
                start_date = schedule.get('start_date', '')
                if start_date:
                    try:
                        date_only = start_date.split('T')[0]
                        by_date[date_only] += 1
                    except:
                        continue
            
            if by_date:
                print(f"\n📅 Hauler 77 schedules by date:")
                for date, count in sorted(by_date.items()):
                    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    marker = " ← TOMORROW!" if date == tomorrow else ""
                    print(f"  {date}: {count} schedules{marker}")
            
        else:
            print(f"❌ HAULER 77 NOT FOUND in schedules")
            print(f"🤔 Possible reasons:")
            print(f"   - Different hauler number in scheduling system")
            print(f"   - No schedules created yet for hauler 77")
            print(f"   - Hauler 77 routes are managed differently")
            
            # Look for similar names
            print(f"\n🔍 Looking for haulers with similar names...")
            target_keywords = ['arizona', 'milk', 'transport', '77']
            
            for hauler_num, details in hauler_details.items():
                name_lower = details.get('name', '').lower()
                matches = sum(1 for keyword in target_keywords if keyword in name_lower)
                if matches > 0:
                    print(f"   Hauler {hauler_num}: {details.get('name')} (matches: {matches})")
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    analyze_schedule_haulers() 