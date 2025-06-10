import requests
import json
from datetime import datetime

# Test the routes API
def test_routes_api():
    base_url = "http://localhost:8000"
    
    # Test authentication first
    print("=== TESTING ROUTES API ===")
    
    # Login to get token
    login_data = {"username": "admin", "password": "admin123"}
    print("1. Attempting login...")
    
    try:
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            response_data = login_response.json()
            token = response_data.get("access_token") or response_data.get("token") or response_data.get("jwt")
            
            if token:
                print(f"Got token: {token[:20]}...")
                headers = {"Authorization": f"Bearer {token}"}
                
                # Test current system date
                print(f"\n2. Testing date logic...")
                print(f"Container thinks today is: {datetime.now()}")
                
                # Test with today (should return June 9th data)
                print(f"\n3. Testing routes for tk_farms TODAY...")
                routes_response = requests.get(f"{base_url}/api/routes/tk_farms/today", headers=headers)
                print(f"Routes status: {routes_response.status_code}")
                
                if routes_response.status_code == 200:
                    routes_data = routes_response.json()
                    print(f"API says date is: {routes_data.get('date')}")
                    print(f"Routes count: {len(routes_data.get('routes', []))}")
                else:
                    print(f"Error: {routes_response.text}")
                
                # Test with explicit June 9th
                print(f"\n4. Testing routes for tk_farms on 2025-06-09...")
                routes_response = requests.get(f"{base_url}/api/routes/tk_farms/today?target_date=2025-06-09", headers=headers)
                print(f"Routes status: {routes_response.status_code}")
                
                if routes_response.status_code == 200:
                    routes_data = routes_response.json()
                    print(f"API says date is: {routes_data.get('date')}")
                    print(f"Routes count: {len(routes_data.get('routes', []))}")
                    if routes_data.get('routes'):
                        print(f"First route: {routes_data['routes'][0].get('route_number')} - {routes_data['routes'][0].get('driver_name')}")
                else:
                    print(f"Error: {routes_response.text}")
                    
                # Test with explicit June 10th
                print(f"\n5. Testing routes for tk_farms on 2025-06-10...")
                routes_response = requests.get(f"{base_url}/api/routes/tk_farms/today?target_date=2025-06-10", headers=headers)
                print(f"Routes status: {routes_response.status_code}")
                
                if routes_response.status_code == 200:
                    routes_data = routes_response.json()
                    print(f"API says date is: {routes_data.get('date')}")
                    print(f"Routes count: {len(routes_data.get('routes', []))}")
                else:
                    print(f"Error: {routes_response.text}")
                    
            else:
                print("No token found in response!")
            
        else:
            print(f"Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_routes_api() 