import requests
import json
from datetime import datetime, timedelta

# Samsara API configuration
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
VOLUME_FORM_TEMPLATE_ID = "3eb6b1ea-588f-4a46-b405-a3858ae7422e"

headers = {
    "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
    "Accept": "application/json"
}

def get_recent_submissions():
    """Get recent form submissions for debugging"""
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
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print(f"Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def analyze_submission_details(submissions):
    """Analyze submission details to understand the data structure"""
    if not submissions:
        print("No submissions found")
        return
    
    print(f"=== ANALYZING {len(submissions)} SUBMISSIONS ===\n")
    
    # Look at first few submissions in detail
    for i, submission in enumerate(submissions[:3]):
        print(f"--- SUBMISSION {i+1} ---")
        print(f"ID: {submission.get('id')}")
        print(f"Status: {submission.get('status')}")
        print(f"Submitted: {submission.get('submittedAtTime')}")
        
        fields = submission.get('fields', [])
        dairy_fields = []
        volume_fields = []
        
        for field in fields:
            label = field.get('label', '').strip()
            field_type = field.get('type')
            field_id = field.get('id')
            
            # Look for dairy selection fields
            if 'dairy' in label.lower():
                dairy_fields.append({
                    'label': label,
                    'type': field_type,
                    'id': field_id,
                    'field': field
                })
            
            # Look for volume fields with actual values
            elif 'volume' in label.lower() and field_type == 'number':
                if 'numberValue' in field and field['numberValue'].get('value') is not None:
                    volume_fields.append({
                        'label': label,
                        'value': field['numberValue'].get('value'),
                        'id': field_id
                    })
        
        print(f"\nDairy Fields Found ({len(dairy_fields)}):")
        for df in dairy_fields:
            print(f"  Label: {df['label']}")
            print(f"  Type: {df['type']}")
            print(f"  ID: {df['id']}")
            
            # Show checkbox details
            if df['type'] == 'check_boxes' and 'checkBoxesValue' in df['field']:
                checkbox_value = df['field']['checkBoxesValue']
                selected = checkbox_value.get('selectedChoices', [])
                print(f"  Selected choices: {len(selected)}")
                for choice in selected:
                    print(f"    - {choice.get('label', 'No label')}")
            print()
        
        print(f"Volume Fields with Values ({len(volume_fields)}):")
        for vf in volume_fields:
            print(f"  {vf['label']:30} = {vf['value']:>8,} lbs")
        
        print(f"{'='*60}\n")

def get_form_template_choices():
    """Get the form template to see available choices"""
    url = f"https://api.samsara.com/form-templates/{VOLUME_FORM_TEMPLATE_ID}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            template = response.json()
            print(f"=== FORM TEMPLATE ANALYSIS ===")
            print(f"Name: {template.get('name', 'N/A')}")
            
            fields = template.get('fields', [])
            for field in fields:
                label = field.get('label', '').strip()
                field_type = field.get('type')
                
                if 'dairy' in label.lower() and field_type == 'check_boxes':
                    print(f"\nDairy Field: {label}")
                    choices = field.get('options', {}).get('choices', [])
                    print(f"Available choices ({len(choices)}):")
                    for choice in choices:
                        print(f"  - {choice.get('label', 'No label')}")
                    break
        else:
            print(f"Template Error: {response.status_code}")
    except Exception as e:
        print(f"Template Error: {e}")

def find_submissions_with_data():
    """Find submissions that have actual data"""
    url = "https://api.samsara.com/form-submissions/stream"
    
    end_time = datetime.now()
    start_time = end_time - timedelta(days=3)  # Look back 3 days
    
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    params = {
        'startTime': start_time_str,
        'endTime': end_time_str,
        'formTemplateIds': VOLUME_FORM_TEMPLATE_ID
    }
    
    submissions_with_volumes = []
    
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            all_submissions = data.get('data', [])
            
            print(f"=== SCANNING {len(all_submissions)} SUBMISSIONS FOR DATA ===")
            
            for submission in all_submissions:
                fields = submission.get('fields', [])
                has_volume_data = False
                volume_count = 0
                
                for field in fields:
                    if (field.get('type') == 'number' and 
                        'volume' in field.get('label', '').lower() and
                        'numberValue' in field and 
                        field['numberValue'].get('value') is not None):
                        has_volume_data = True
                        volume_count += 1
                
                if has_volume_data:
                    submissions_with_volumes.append({
                        'submission': submission,
                        'volume_count': volume_count,
                        'timestamp': submission.get('submittedAtTime')
                    })
            
            print(f"Found {len(submissions_with_volumes)} submissions with volume data")
            
            # Show the ones with the most volume data
            submissions_with_volumes.sort(key=lambda x: x['volume_count'], reverse=True)
            
            for i, sub_data in enumerate(submissions_with_volumes[:3]):
                submission = sub_data['submission']
                print(f"\n--- HIGH-DATA SUBMISSION {i+1} ---")
                print(f"Volume fields: {sub_data['volume_count']}")
                print(f"Time: {sub_data['timestamp']}")
                print(f"ID: {submission.get('id')}")
                
                # Show all volume values
                fields = submission.get('fields', [])
                for field in fields:
                    if (field.get('type') == 'number' and 
                        'volume' in field.get('label', '').lower() and
                        'numberValue' in field and 
                        field['numberValue'].get('value') is not None):
                        
                        label = field.get('label', '')
                        value = field['numberValue'].get('value')
                        print(f"  {label:25} = {value:>8,} lbs")
            
            return submissions_with_volumes
        else:
            print(f"Error: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    print("🔍 DEBUGGING SAMSARA FORM SUBMISSIONS")
    print("=" * 50)
    
    # 1. Get form template to see available choices
    get_form_template_choices()
    
    # 2. Get recent submissions for analysis
    print(f"\n{'='*50}")
    submissions = get_recent_submissions()
    
    # 3. Analyze submission details
    analyze_submission_details(submissions)
    
    # 4. Find submissions with actual volume data
    print(f"\n{'='*50}")
    find_submissions_with_data() 