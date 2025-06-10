import requests
import json
from datetime import datetime, timedelta

# Samsara API configuration
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
headers = {
    "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
    "Accept": "application/json"
}

def get_form_templates():
    """Get all form templates from Samsara"""
    url = "https://api.samsara.com/form-templates"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        templates = response.json().get('data', [])
        print(f"=== FORM TEMPLATES ({len(templates)} total) ===")
        for template in templates:
            print(f"ID: {template.get('id')}")
            print(f"Name: {template.get('name', 'N/A')}")
            print(f"Description: {template.get('description', 'N/A')}")
            print("-" * 50)
        return templates
    except requests.exceptions.RequestException as e:
        print(f"Error getting form templates: {e}")
        return []

def get_template_details(template_id):
    """Get detailed structure of a specific form template"""
    url = f"https://api.samsara.com/form-templates/{template_id}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        template = response.json()
        
        print(f"\n=== TEMPLATE DETAILS: {template_id} ===")
        print(f"Name: {template.get('name', 'N/A')}")
        print(f"Description: {template.get('description', 'N/A')}")
        print(f"Fields:")
        
        fields = template.get('fields', [])
        for i, field in enumerate(fields):
            print(f"  {i+1}. {field.get('label', 'No label')} ({field.get('type')})")
            
        return template
    except requests.exceptions.RequestException as e:
        print(f"Error getting template details: {e}")
        return None

def get_form_submissions(template_id=None, limit=5):
    """Get recent form submissions"""
    url = "https://api.samsara.com/form-submissions"
    params = {}
    if limit:
        params['limit'] = limit
        
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        submissions = response.json().get('data', [])
        
        print(f"\n=== RECENT FORM SUBMISSIONS ({len(submissions)} shown) ===")
        for submission in submissions:
            print(f"ID: {submission.get('id')}")
            print(f"Template: {submission.get('formTemplate', {}).get('name', 'N/A')}")
            print(f"Status: {submission.get('status')}")
            print(f"Submitted: {submission.get('submittedAtTime')}")
            print(f"Fields: {len(submission.get('fields', []))} fields")
            print("-" * 50)
            
        return submissions
    except requests.exceptions.RequestException as e:
        print(f"Error getting form submissions: {e}")
        return []

def test_form_submissions_endpoint():
    """Test different ways to access form submissions"""
    print("=== TESTING FORM SUBMISSIONS API ===")
    
    # Try 1: Basic form submissions without parameters
    print("\n1. Testing basic form submissions endpoint...")
    url = "https://api.samsara.com/form-submissions"
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 400:
            print("400 Error - might need specific parameters")
            print(f"Response: {response.text[:200]}...")
        elif response.status_code == 200:
            data = response.json()
            print(f"Success! Found {len(data.get('data', []))} submissions")
    except Exception as e:
        print(f"Error: {e}")
    
    # Try 2: With startMs and endMs parameters (common in Samsara API)
    print("\n2. Testing with time range parameters...")
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)  # Last 7 days
    
    params = {
        'startMs': int(start_time.timestamp() * 1000),
        'endMs': int(end_time.timestamp() * 1000)
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            submissions = data.get('data', [])
            print(f"Success! Found {len(submissions)} submissions in last 7 days")
            
            # Show details of first few submissions
            for i, submission in enumerate(submissions[:3]):
                print(f"\nSubmission {i+1}:")
                print(f"  ID: {submission.get('id')}")
                print(f"  Status: {submission.get('status')}")
                print(f"  Template ID: {submission.get('formTemplate', {}).get('id')}")
                print(f"  Submitted: {submission.get('submittedAtTime')}")
                print(f"  Fields: {len(submission.get('fields', []))}")
                
                # Show field details
                fields = submission.get('fields', [])
                for j, field in enumerate(fields[:5]):  # Show first 5 fields
                    label = field.get('label', 'No label')
                    field_type = field.get('type', 'unknown')
                    print(f"    Field {j+1}: {label} ({field_type})")
                    
                if len(fields) > 5:
                    print(f"    ... and {len(fields) - 5} more fields")
                    
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

def test_with_specific_ids():
    """Test the API with specific form submission IDs if we can find any"""
    print("\n=== TESTING WITH SPECIFIC IDS ===")
    
    # The API documentation mentions we need specific IDs
    # Let's see if we can get submissions another way
    
    # Try to get all form templates with different approach
    print("\n3. Testing form templates with minimal parameters...")
    url = "https://api.samsara.com/form-templates"
    try:
        # Try with minimal query parameters
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            print(f"Found {len(templates)} templates")
            
            # Try to get first template with additional info
            if templates:
                template_id = templates[0].get('id')
                print(f"\n4. Testing individual template access: {template_id}")
                detail_url = f"https://api.samsara.com/form-templates/{template_id}"
                
                # Try with include parameter
                params = {'include': 'externalIds'}
                detail_response = requests.get(detail_url, headers=headers, params=params)
                print(f"Detail Status: {detail_response.status_code}")
                
                if detail_response.status_code == 200:
                    template_detail = detail_response.json()
                    print(f"Template Name: {template_detail.get('name', 'N/A')}")
                    print(f"Fields: {len(template_detail.get('fields', []))}")
                else:
                    print(f"Detail Error: {detail_response.text[:200]}...")
        else:
            print(f"Templates Error: {response.text[:200]}...")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_form_submissions_endpoint()
    test_with_specific_ids() 