#!/usr/bin/env python3
"""
Debug script to check raw data formats from both APIs
"""
import requests
import json
from datetime import datetime

# Test what the actual API returns
API_BASE_URL = 'https://api.prod.milkmoovement.io/v1'
API_TOKEN = 'amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM'
headers = {'X-API-KEY': API_TOKEN}

print('=== CHECKING RAW PICKUP DATA ===')
today = datetime.now().strftime('%Y-%m-%d')
response = requests.get(f'{API_BASE_URL}/pickups/load-summary', headers=headers, params={'start_date': today, 'end_date': today})
if response.status_code == 200:
    pickups = response.json()
    if pickups:
        print(f'Found {len(pickups)} pickup records')
        print(f'First pickup record:')
        first_pickup = pickups[0]
        for key, value in first_pickup.items():
            print(f'  {key}: {value} ({type(value).__name__})')
            
        # Check for hauler 77 specifically
        hauler_77 = [p for p in pickups if str(p.get('hauler_number', '')) == '77']
        if hauler_77:
            print(f'\nFirst hauler 77 pickup:')
            for key, value in hauler_77[0].items():
                print(f'  {key}: {value} ({type(value).__name__})')
    else:
        print('No pickup data')
else:
    print(f'Pickup API error: {response.status_code}')

print('\n=== CHECKING RAW SCHEDULE DATA ===')
response = requests.get(f'{API_BASE_URL}/schedules', headers=headers, params={'start_date': today, 'end_date': today})
if response.status_code == 200:
    schedules = response.json()
    if schedules:
        print(f'Found {len(schedules)} schedule records')
        print(f'First schedule record:')
        first_schedule = schedules[0]
        for key, value in first_schedule.items():
            print(f'  {key}: {value} ({type(value).__name__})')
            
        # Check for hauler 77 specifically
        hauler_77_schedules = []
        for schedule in schedules:
            hauler_info = schedule.get('hauler', {})
            if str(hauler_info.get('hauler_number', '')) == '77':
                hauler_77_schedules.append(schedule)
        
        if hauler_77_schedules:
            print(f'\nFirst hauler 77 schedule:')
            for key, value in hauler_77_schedules[0].items():
                print(f'  {key}: {value} ({type(value).__name__})')
    else:
        print('No schedule data')
else:
    print(f'Schedule API error: {response.status_code}') 