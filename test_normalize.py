#!/usr/bin/env python3

import re

def normalize_dairy_name(dairy_name):
    """Normalize dairy names to handle various building/facility variations"""
    if not dairy_name:
        return dairy_name
    
    # Handle T&K specific case first (most common in your logs)
    if dairy_name.startswith('T&K '):
        return 'T&K'
    
    # General patterns to remove facility/building identifiers
    # Pattern 1: "Dairy Name - Building Type #" or "Dairy Name - Building Type"
    separators = [' - ', ' – ', ' — ']  # different dash types
    building_keywords = ['barn', 'parlor', 'facility', 'site', 'location', 'building', 'milking']
    
    for separator in separators:
        if separator in dairy_name.lower():
            parts = dairy_name.split(separator)
            if len(parts) >= 2:
                # Check if the second part looks like a building identifier
                second_part = parts[1].lower().strip()
                if any(keyword in second_part for keyword in building_keywords):
                    return parts[0].strip()
                # Also check for just numbers (like "Site 1", "Building 2")
                if re.match(r'^(site|building|barn|parlor|facility|location)\s*\d+$', second_part):
                    return parts[0].strip()
    
    # Pattern 2: "Dairy Name (Building info)" - remove parenthetical building info
    parenthetical_patterns = [
        r'\s*\([^)]*(?:barn|parlor|facility|site|location|building|milking)\s*[^)]*\)',  # (Barn 1), (Milking Facility), etc.
        r'\s*\(\d+\)\s*-\s*(?:barn|parlor|facility|site|location|building)',  # (348) - Barn
        r'\s*\([^)]*\d+[^)]*\)$'  # Generic (###) at end
    ]
    
    for pattern in parenthetical_patterns:
        dairy_name = re.sub(pattern, '', dairy_name, flags=re.IGNORECASE)
    
    # Pattern 3: "Dairy Name Building# or Dairy#" - handle space-separated building numbers
    space_patterns = [
        r'\s+(?:barn|parlor|facility|site|location|building|milking)\s*\d+$',  # "Barn 1", "Facility 2"
        r'\s+(?:barn|parlor|facility|site|location|building|milking)$',  # Just "Barn", "Facility"
        r'\s+(?:barn|parlor|facility|site|location|building|milking)\s+[A-Z]$',  # "Location A", "Site B"
    ]
    
    for pattern in space_patterns:
        dairy_name = re.sub(pattern, '', dairy_name, flags=re.IGNORECASE)
    
    # Pattern 4: Handle specific building/location patterns that end names
    # Only remove trailing single letters/numbers if they're clearly building identifiers
    end_building_patterns = [
        r'\s+(?:barn|parlor|facility|site|location|building|milking)\s+[A-Z]\s*$',  # "Location A", "Site B"
        r'\s+(?:barn|parlor|facility|site|location|building|milking)\s+\d+\s*$',    # "Barn 1", "Site 2"
    ]
    
    for pattern in end_building_patterns:
        dairy_name = re.sub(pattern, '', dairy_name, flags=re.IGNORECASE)
    
    # Clean up extra whitespace
    dairy_name = ' '.join(dairy_name.split())
    
    return dairy_name.strip()

# Test cases
test_cases = [
    # T&K variations
    "T&K (348) - Barn 1",
    "T&K (348) - Barn 2",
    "T&K (348) - Barn 3",
    
    # Other common patterns
    "Milky Way Dairy - Barn 1",
    "Sunshine Farms - Parlor 2",
    "Triple A Dairy - Facility 3",
    "Green Valley (123) - Milking Facility",
    "Happy Cow Dairy (Barn A)",
    "Mountain View Dairy Barn 5",
    "Desert Dairy Facility",
    "Ocean View Dairy Site 2",
    
    # Edge cases
    "Dairy 21",  # Should keep numbers that are part of name
    "Farm 365 - Barn 1",  # Should remove barn but keep farm number
    "ABC Dairy",  # No building info, should stay same
    "XYZ Farm Location A",  # Should remove location
    "Quick Stop Dairy Building",  # Should remove building
]

print("🧪 TESTING DAIRY NAME NORMALIZATION")
print("=" * 50)

for test_case in test_cases:
    normalized = normalize_dairy_name(test_case)
    print(f"'{test_case}' → '{normalized}'") 