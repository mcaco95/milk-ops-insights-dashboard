import requests
import os
import json
from datetime import datetime, timedelta

# --- Configuration ---
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

def get_auth_headers():
    """Returns the authorization headers for the Samsara API request."""
    return {
        "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
        "Accept": "application/json"
    }

def list_samsara_routes():
    """
    Fetches a list of routes from the Samsara API and prints the first one found.
    """
    print("Attempting to fetch a list of routes from Samsara...")
    # This is the standard endpoint for listing resources.
    url = "https://api.samsara.com/fleet/routes"
    
    # --- FIX: Add required time range parameters ---
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=7)
    params = {
        "startTime": start_time.isoformat() + "Z",
        "endTime": end_time.isoformat() + "Z"
    }
    
    try:
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        routes = response.json().get('data', [])
        
        if not routes:
            print("No routes found in your Samsara account for the default time range.")
            return

        print("\n\n>>> --- Raw Data for First Found Samsara Route --- <<<")
        print(json.dumps(routes[0], indent=4))
        print(">>> ---------------------------------------------- <<<\n\n")

    except requests.exceptions.RequestException as e:
        print(f"FATAL: Could not get routes from Samsara: {e}")
        if response is not None:
            print(f"Response Text: {response.text}")

if __name__ == "__main__":
    list_samsara_routes() 