#!/usr/bin/env python3

import sys
import os

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tank_level_dashboard import get_volume_submissions, parse_submission_volumes

def compare_barn_parsing():
    """Compare parsing between working barns and T&K Barn 2"""
    print("=== COMPARING BARN PARSING ===\n")
    
    submissions = get_volume_submissions(hours_back=24)
    
    # Find latest submissions for different barns
    barn_submissions = {}
    
    for submission in submissions:
        parsed = parse_submission_volumes(submission)
        dairy = parsed.get('dairy')
        
        if dairy and dairy.startswith('T&K'):
            if dairy not in barn_submissions:
                barn_submissions[dairy] = {
                    'parsed': parsed,
                    'raw': submission
                }
    
    print(f"Found barns: {list(barn_submissions.keys())}\n")
    
    for dairy_name, data in barn_submissions.items():
        print(f"=== {dairy_name} ===")
        parsed = data['parsed']
        raw = data['raw']
        
        print(f"Parsed milking_into: '{parsed['milking_into']}'")
        print(f"Parsed volumes: {parsed['volumes']}")
        
        # Look at raw milking fields
        fields = raw.get('fields', [])
        milking_fields = []
        
        for i, field in enumerate(fields):
            label = field.get('label', '').strip().lower()
            if 'milking' in label and 'into' in label:
                milking_fields.append((i+1, field))
        
        print(f"Raw milking fields found: {len(milking_fields)}")
        
        for idx, field in milking_fields:
            print(f"  Field {idx}: '{field['label']}'")
            if 'multipleChoiceValue' in field:
                value = field['multipleChoiceValue'].get('value', 'NO VALUE')
                print(f"    HAS VALUE: '{value}'")
            else:
                print(f"    NO VALUE")
        
        print()
    
    # Let's also look at the specific parsing logic for the milking field
    print("=== TESTING PARSE LOGIC ON T&K BARN 2 ===")
    if 'T&K [Barn 2]' in barn_submissions:
        raw = barn_submissions['T&K [Barn 2]']['raw']
        fields = raw.get('fields', [])
        
        print("Testing our parsing logic manually:")
        milking_into = None
        
        for field in fields:
            label = field.get('label', '').strip()
            field_type = field.get('type')
            
            print(f"  Checking field: '{label}' (type: {field_type})")
            
            # Our current logic
            if 'milking into' in label.lower() and field_type == 'multiple_choice':
                print(f"    MATCHES our logic!")
                if 'multipleChoiceValue' in field:
                    milking_into = field['multipleChoiceValue'].get('value', '')
                    print(f"    Found value: '{milking_into}'")
                else:
                    print(f"    No multipleChoiceValue key")
        
        print(f"Final milking_into result: '{milking_into}'")

if __name__ == "__main__":
    compare_barn_parsing() 