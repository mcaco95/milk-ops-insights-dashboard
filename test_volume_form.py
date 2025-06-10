import requests
import json
from datetime import datetime, timedelta

# Samsara API configuration
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
headers = {
    "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
    "Accept": "application/json"
}

# The volume submission form template ID
VOLUME_FORM_TEMPLATE_ID = "3eb6b1ea-588f-4a46-b405-a3858ae7422e"

def get_volume_form_template():
    """Get the detailed structure of the volume submission form"""
    print("=== VOLUME SUBMISSION FORM TEMPLATE ===")
    url = f"https://api.samsara.com/form-templates/{VOLUME_FORM_TEMPLATE_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            template = response.json()
            print(f"Name: {template.get('name', 'N/A')}")
            print(f"Description: {template.get('description', 'N/A')}")
            print(f"ID: {template.get('id')}")
            
            print(f"\n=== FORM FIELDS ({len(template.get('fields', []))}) ===")
            fields = template.get('fields', [])
            for i, field in enumerate(fields):
                print(f"{i+1:2d}. {field.get('label', 'No label'):30} ({field.get('type'):15}) ID: {field.get('id')}")
                
                # Show additional details for specific field types
                if field.get('type') == 'multiple_choice':
                    choices = field.get('options', {}).get('choices', [])
                    if choices:
                        choice_labels = [choice.get('label') for choice in choices[:5]]
                        print(f"     Choices: {choice_labels}")
                        if len(choices) > 5:
                            print(f"              ... and {len(choices) - 5} more")
                            
                elif field.get('type') == 'number':
                    number_options = field.get('options', {})
                    if number_options:
                        print(f"     Number options: {number_options}")
                        
            return template
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_volume_form_submissions_stream():
    """Get volume form submissions using the stream endpoint"""
    print("\n=== VOLUME FORM SUBMISSIONS (STREAM) ===")
    
    # Use the stream endpoint with time range and form template filter
    url = "https://api.samsara.com/form-submissions/stream"
    
    # Get submissions from last 7 days
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    # Format times in RFC 3339 format as required
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    params = {
        'startTime': start_time_str,
        'endTime': end_time_str,
        'formTemplateIds': VOLUME_FORM_TEMPLATE_ID
    }
    
    print(f"Time range: {start_time_str} to {end_time_str}")
    print(f"Template ID: {VOLUME_FORM_TEMPLATE_ID}")
    
    try:
        response = requests.get(url, headers=headers, params=params)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            submissions = data.get('data', [])
            
            print(f"Found {len(submissions)} volume form submissions in last 7 days")
            
            if submissions:
                print(f"\n=== SUBMISSION DETAILS ===")
                for i, submission in enumerate(submissions[:3]):  # Show first 3 submissions
                    print(f"\n--- SUBMISSION {i+1} ---")
                    print(f"ID: {submission.get('id')}")
                    print(f"Status: {submission.get('status')}")
                    print(f"Submitted: {submission.get('submittedAtTime')}")
                    print(f"Updated: {submission.get('updatedAtTime')}")
                    print(f"Submitted by: {submission.get('submittedBy', {}).get('name', 'N/A')}")
                    
                    # Show field values
                    fields = submission.get('fields', [])
                    print(f"Fields ({len(fields)}):")
                    for j, field in enumerate(fields):
                        label = field.get('label', 'No label')
                        field_type = field.get('type', 'unknown')
                        field_id = field.get('id', 'N/A')
                        
                        # Get the field value based on type
                        value = "N/A"
                        if field_type == 'text' and 'textValue' in field:
                            value = field['textValue'].get('value', 'N/A')
                        elif field_type == 'number' and 'numberValue' in field:
                            value = field['numberValue'].get('value', 'N/A')
                        elif field_type == 'multiple_choice' and 'multipleChoiceValue' in field:
                            selected = field['multipleChoiceValue'].get('selectedChoices', [])
                            value = [choice.get('label') for choice in selected]
                        elif field_type == 'datetime' and 'dateTimeValue' in field:
                            value = field['dateTimeValue'].get('value', 'N/A')
                        elif field_type == 'check_boxes' and 'checkBoxesValue' in field:
                            checked = field['checkBoxesValue'].get('selectedChoices', [])
                            value = [choice.get('label') for choice in checked]
                        
                        print(f"  {j+1:2d}. {label:25} = {value}")
                        print(f"      (Type: {field_type}, ID: {field_id})")
                
                # Show pagination info if available
                pagination = data.get('pagination', {})
                if pagination:
                    print(f"\n=== PAGINATION ===")
                    print(f"Has next page: {pagination.get('hasNextPage', False)}")
                    if pagination.get('endCursor'):
                        print(f"End cursor: {pagination.get('endCursor')}")
                        
            return submissions
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_volume_data_structure(submissions):
    """Analyze the structure of volume submissions to understand the data format"""
    if not submissions:
        return
        
    print(f"\n=== VOLUME DATA ANALYSIS ===")
    
    # Look for common field patterns across submissions
    all_field_labels = set()
    all_field_types = set()
    field_frequency = {}
    
    for submission in submissions:
        fields = submission.get('fields', [])
        for field in fields:
            label = field.get('label', '')
            field_type = field.get('type', '')
            
            all_field_labels.add(label)
            all_field_types.add(field_type)
            
            key = f"{label} ({field_type})"
            field_frequency[key] = field_frequency.get(key, 0) + 1
    
    print(f"Unique field labels found: {len(all_field_labels)}")
    print(f"Field types used: {list(all_field_types)}")
    
    print(f"\n=== MOST COMMON FIELDS ===")
    sorted_fields = sorted(field_frequency.items(), key=lambda x: x[1], reverse=True)
    for field_info, count in sorted_fields[:10]:
        print(f"{count:2d}x {field_info}")
    
    # Look for volume-related fields
    volume_keywords = ['volume', 'amount', 'quantity', 'milk', 'gallons', 'pounds', 'lbs', 'tank']
    print(f"\n=== POTENTIAL VOLUME FIELDS ===")
    for label in all_field_labels:
        if any(keyword.lower() in label.lower() for keyword in volume_keywords):
            print(f"- {label}")

if __name__ == "__main__":
    # Get the form template structure first
    template = get_volume_form_template()
    
    # Get recent volume submissions using the stream endpoint
    submissions = get_volume_form_submissions_stream()
    
    # Analyze the data structure
    if submissions:
        analyze_volume_data_structure(submissions)
    
    print(f"\n=== SUMMARY ===")
    print(f"Template loaded: {'Yes' if template else 'No'}")
    print(f"Volume submissions found: {len(submissions) if submissions else 0}")
    if submissions:
        print("Success! We can now access volume submission data for the tank level system.") 