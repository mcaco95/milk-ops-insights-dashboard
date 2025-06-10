#!/usr/bin/env python3
"""
Local debug script to test date parsing
"""
import requests
import pandas as pd
from datetime import datetime

# Test what the actual API returns
API_BASE_URL = 'https://api.prod.milkmoovement.io/v1'
API_TOKEN = 'amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM'
headers = {'X-API-KEY': API_TOKEN}

print('=== TESTING DATE PARSING ===')

# Test some example date formats we might get
test_dates = [
    "2025-06-09T07:00:00Z",
    "2025-06-09T07:00:00",
    "2025-06-09 07:00:00",
    "07:00:00",
    None,
    ""
]

def test_date_parsing(pickup_date_raw):
    """Test the same parsing logic from the script"""
    start_time = 'N/A'
    try:
        if pickup_date_raw:
            # Try to parse the date - handle both formats
            if isinstance(pickup_date_raw, str):
                # Handle ISO format: "2025-06-09T07:00:00Z" or "2025-06-09T07:00:00"
                if 'T' in pickup_date_raw:
                    date_part, time_part = pickup_date_raw.split('T')
                    time_only = time_part.split('Z')[0].split('.')[0]  # Remove timezone and microseconds
                    hour_min = time_only[:5]  # Get HH:MM
                    start_time = hour_min
                else:
                    # Try direct parsing
                    parsed_date = pd.to_datetime(pickup_date_raw)
                    start_time = parsed_date.strftime('%H:%M')
            else:
                # Already a datetime object
                parsed_date = pd.to_datetime(pickup_date_raw)
                start_time = parsed_date.strftime('%H:%M')
    except Exception as e:
        print(f"ERROR parsing '{pickup_date_raw}': {e}")
        start_time = 'ERROR'
    
    return start_time

print("Testing different date formats:")
for test_date in test_dates:
    result = test_date_parsing(test_date)
    print(f"Input: {test_date} -> Output: {result}")

print("\n=== CHECKING ACTUAL API DATA ===")
today = datetime.now().strftime('%Y-%m-%d')

# Check pickups
try:
    response = requests.get(f'{API_BASE_URL}/pickups/load-summary', headers=headers, params={'start_date': today, 'end_date': today})
    if response.status_code == 200:
        pickups = response.json()
        hauler_77 = [p for p in pickups if str(p.get('hauler_number', '')) == '77']
        if hauler_77:
            pickup = hauler_77[0]
            pickup_date = pickup.get('pickup_date')
            print(f"PICKUP DATE: {pickup_date} ({type(pickup_date)})")
            print(f"PARSED: {test_date_parsing(pickup_date)}")
except Exception as e:
    print(f"Pickup API error: {e}")

# Check schedules  
try:
    response = requests.get(f'{API_BASE_URL}/schedules', headers=headers, params={'start_date': today, 'end_date': today})
    if response.status_code == 200:
        schedules = response.json()
        hauler_77_schedules = []
        for schedule in schedules:
            hauler_info = schedule.get('hauler', {})
            if str(hauler_info.get('hauler_number', '')) == '77':
                hauler_77_schedules.append(schedule)
        
        if hauler_77_schedules:
            schedule = hauler_77_schedules[0]
            start_date = schedule.get('start_date')
            print(f"SCHEDULE START_DATE: {start_date} ({type(start_date)})")
            print(f"PARSED: {test_date_parsing(start_date)}")
except Exception as e:
    print(f"Schedule API error: {e}") 