import requests

# API credentials
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

def get_auth_headers():
    return {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}

def find_truck_by_name(truck_name):
    """Find a truck by searching for its name."""
    print(f"Searching for truck: {truck_name}")
    search_url = f"https://api.samsara.com/fleet/vehicles?search={truck_name}"
    
    try:
        response = requests.get(search_url, headers=get_auth_headers())
        response.raise_for_status()
        vehicles = response.json().get('data', [])
        
        if vehicles:
            vehicle = vehicles[0]
            print(f"Found truck: {vehicle['name']} (ID: {vehicle['id']})")
            return vehicle['id']
        else:
            print(f"No truck found with name: {truck_name}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error searching for truck: {e}")
        return None

def get_truck_stats(vehicle_id):
    """Get GPS and speed stats for a specific vehicle."""
    print(f"Getting stats for vehicle ID: {vehicle_id}")
    
    # Try different ways to format the request
    stats_url = "https://api.samsara.com/fleet/vehicles/stats"
    
    # Method 1: vehicleIds as comma-separated string
    params1 = {
        "vehicleIds": vehicle_id,
        "types": "gps,ecuSpeedMph"
    }
    
    print(f"Trying method 1 - vehicleIds as string")
    print(f"URL: {stats_url}")
    print(f"Params: {params1}")
    
    try:
        response = requests.get(stats_url, headers=get_auth_headers(), params=params1)
        print(f"Response status: {response.status_code}")
        print(f"Response URL: {response.url}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS! Raw response: {data}")
            return data
        else:
            print(f"Error response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
    
    return None

def main():
    # Test with a known truck number
    truck_names_to_try = ["422", "DMT 422", "TRUCK 422", "416", "DMT 416"]
    
    for truck_name in truck_names_to_try:
        vehicle_id = find_truck_by_name(truck_name)
        if vehicle_id:
            print(f"\n--- Testing stats API for {truck_name} (ID: {vehicle_id}) ---")
            stats = get_truck_stats(vehicle_id)
            if stats:
                break
            print("Trying next truck name...\n")
        else:
            print(f"Truck {truck_name} not found, trying next...\n")

if __name__ == "__main__":
    main() 