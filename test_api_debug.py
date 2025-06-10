#!/usr/bin/env python3
"""
Test Samsara API directly to see what's going wrong
"""

import requests
from datetime import datetime, timedelta

# Samsara API configuration
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
VOLUME_FORM_TEMPLATE_ID = "3eb6b1ea-588f-4a46-b405-a3858ae7422e"

headers = {
    "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
    "Accept": "application/json"
}

def test_samsara_api():
    """Test Samsara API directly"""
    print("=== TESTING SAMSARA API ===\n")
    
    url = "https://api.samsara.com/form-submissions/stream"
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=24)
    
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    params = {
        'startTime': start_time_str,
        'endTime': end_time_str,
        'formTemplateIds': VOLUME_FORM_TEMPLATE_ID
    }
    
    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Params: {params}")
    print()
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print(f"Response Data Keys: {list(data.keys())}")
            
            submissions = data.get('data', [])
            print(f"Submissions Count: {len(submissions)}")
            
            if submissions:
                print(f"\nFirst Submission:")
                first = submissions[0]
                print(f"  Keys: {list(first.keys())}")
                print(f"  ID: {first.get('id')}")
                print(f"  Status: {first.get('status')}")
                print(f"  Submitted: {first.get('submittedAtTime')}")
                print(f"  Fields Count: {len(first.get('fields', []))}")
                
                # Show first few fields
                fields = first.get('fields', [])
                for i, field in enumerate(fields[:3]):
                    print(f"  Field {i+1}: {field.get('label')} ({field.get('type')})")
                    
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_samsara_api() 