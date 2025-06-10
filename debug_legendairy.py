import sys
sys.path.append('/app')
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes

print("=== DEBUGGING LEGENDAIRY MILKING ISSUE ===")
submissions = get_volume_submissions(hours_back=48)
print(f"Found {len(submissions)} total submissions")

legendairy_subs = []
for submission in submissions:
    parsed = parse_submission_volumes(submission)
    if parsed.get('dairy') == 'Legendairy LLC':
        legendairy_subs.append({
            'parsed': parsed,
            'raw_fields': submission.get('fields', [])
        })

print(f"\nFound {len(legendairy_subs)} Legendairy submissions")

if legendairy_subs:
    print("\n=== LATEST LEGENDAIRY SUBMISSION ===")
    latest = legendairy_subs[0]
    parsed = latest['parsed']
    
    print(f"Dairy: {parsed.get('dairy')}")
    print(f"Volumes: {parsed.get('volumes')}")
    print(f"Milking Into: {parsed.get('milking_into')}")
    print(f"Pulled From: {parsed.get('pulled_from')}")
    print(f"Timestamp: {parsed.get('timestamp')}")
    
    print(f"\n=== RAW FORM FIELDS ===")
    for i, field in enumerate(latest['raw_fields']):
        label = field.get('label', 'NO_LABEL')
        field_type = field.get('type', 'NO_TYPE')
        
        # Show all fields to understand the structure
        print(f"Field {i}: {field_type} - '{label}'")
        
        # Show the actual values
        if field_type == 'multiple_choice':
            value = field.get('multipleChoiceValue', {}).get('value', 'NO_VALUE')
            print(f"    Value: '{value}'")
        elif field_type == 'number':
            value = field.get('numberValue', {}).get('value', 'NO_VALUE')
            print(f"    Value: {value}")
        elif field_type == 'check_boxes':
            value = field.get('checkBoxesValue', {}).get('value', 'NO_VALUE')
            print(f"    Value: {value}")
        
        # Check if this might be a milking field
        if 'milk' in label.lower():
            print(f"    *** POTENTIAL MILKING FIELD ***")
            print(f"    Full field: {field}")
else:
    print("No Legendairy submissions found!") 