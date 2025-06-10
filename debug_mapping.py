#!/usr/bin/env python3

from get_dairy_volume import get_load_summaries, process_load_summaries
import pandas as pd

# Test mapping
DAIRY_NAME_MAPPING = {
    "Arizona Dairy": "az_dairy",
    "Belmont Dairy(701)": "belmont",
    "D&I Dairy (805)": "d_i_dairy",
    "D&I Holsteins (716)": "d_i_holsteins",
    "Dickman and Sons Dairy (815)": "dickman",
    "Legendairy LLC": "legendairy",
    "Milky Way Dairy (633)": "milky_way",
    "Piazzo Dairy (800)": "piazzo",
    "T&K": "tk_farms",
    "Triple G Dairy": "triple_g"
}

print("=== DEBUGGING DAIRY MAPPING (FULL MONTH) ===")

# Get first week of May
print("Fetching real API data for full week...")
summaries = get_load_summaries('2025-05-01', '2025-05-07')

if summaries:
    df = pd.DataFrame(summaries)
    unique_producers = df['producer_name'].unique()
    
    print(f"\nFound {len(unique_producers)} unique producers:")
    
    # Check specifically for our target dairies
    target_dairies = list(DAIRY_NAME_MAPPING.keys())
    print(f"\n=== Checking for TARGET dairies ===")
    for dairy in target_dairies:
        is_present = dairy in unique_producers
        print(f"'{dairy}' -> Present: {is_present}")
    
    print(f"\n=== ALL PRODUCERS in data ===")
    for i, producer in enumerate(unique_producers):
        mapped = producer in DAIRY_NAME_MAPPING
        print(f"{i+1:2d}. '{producer}' -> Mapped: {mapped}")
    
    print(f"\n=== TESTING process_load_summaries with mapping ===")
    result = process_load_summaries(summaries, DAIRY_NAME_MAPPING)
    print(f"Result: {len(result)} dairies mapped successfully")
    for dairy_id, handlers in result.items():
        total_volume = sum(handlers.values())
        print(f"  {dairy_id}: {total_volume:,.0f} lbs")
    
else:
    print("No summaries found!") 