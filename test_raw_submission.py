import requests
import json

# Samsara API configuration
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

headers = {
    "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
    "Accept": "application/json"
}

def get_raw_submission_data(submission_id):
    """Get raw JSON data for a specific submission"""
    url = "https://api.samsara.com/form-submissions"
    params = {'ids': submission_id}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n=== RAW JSON RESPONSE ===")
            print(json.dumps(data, indent=2))
            
            # Also specifically look at the dairy field
            submissions = data.get('data', [])
            if submissions:
                submission = submissions[0]
                fields = submission.get('fields', [])
                
                print(f"\n=== DAIRY FIELD ANALYSIS ===")
                for i, field in enumerate(fields):
                    label = field.get('label', '').strip()
                    if 'dairy' in label.lower():
                        print(f"Field {i+1}: {label}")
                        print(f"Full field data:")
                        print(json.dumps(field, indent=2))
                        break
            
            return data
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_specific_submissions():
    """Test specific submission IDs we found"""
    test_ids = [
        "9bf342b7-75e0-45d0-bd61-190a590565d7",  # Recent one with Silo volumes
        "6feed918-0713-4879-9526-ab847d45059f",  # Another with Silo volumes
        "96fcd39d-ffd1-4071-9d26-ce6c6cad084a"   # One with Tank volumes
    ]
    
    for i, submission_id in enumerate(test_ids):
        print(f"\n{'='*80}")
        print(f"TESTING SUBMISSION {i+1}: {submission_id}")
        print(f"{'='*80}")
        
        data = get_raw_submission_data(submission_id)
        
        if i < len(test_ids) - 1:  # Don't pause after last one
            input("\nPress Enter to continue to next submission...")

if __name__ == "__main__":
    test_specific_submissions() 