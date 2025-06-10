import requests
import os
from collections import defaultdict
import argparse
import pandas as pd
from datetime import date, timedelta
import calendar

# --- Configuration ---
MILK_MOOVEMENT_API_TOKEN = "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM"
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"
HAULER_NUMBER = "77" # Your specific hauler number
CHUNK_DAYS = 7 # Fetch data in 7-day chunks to reduce API calls

# --- Helper Functions ---
def get_auth_headers():
    """Returns the authorization headers for the API request."""
    return {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}

def get_load_summaries(start_date, end_date):
    """
    Fetches load summary data from the Milk Moovement API for a given date range.
    """
    url = f"{API_BASE_URL}/pickups/load-summary"
    params = {"start_date": start_date, "end_date": end_date}
    
    try:
        response = requests.get(url, headers=get_auth_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching load summaries for {start_date} to {end_date}: {e}")
        return None

def process_load_summaries(summaries):
    """
    Processes load summaries to calculate the total volume per dairy for each handler.
    Filters data for the specific hauler number.
    """
    volume_by_dairy_handler = defaultdict(lambda: defaultdict(float))

    if not summaries:
        return {}

    df = pd.DataFrame(summaries)

    # Ensure required columns exist before proceeding
    required_cols = ['hauler_number', 'producer_name', 'processor_name', 'dropoff_metered']
    if not all(col in df.columns for col in required_cols):
        print("Error: API data is missing required columns ('dropoff_metered'). Cannot process.")
        return {}

    # --- THIS IS THE KEY: Filter for your specific hauler number ---
    df = df[df["hauler_number"] == HAULER_NUMBER]

    if df.empty:
        print(f"No data found for your hauler number ({HAULER_NUMBER}) on the selected date.")
        return {}
    
    # Group by dairy and handler, then sum the volume.
    # fillna(0) handles cases where dropoff_metered might be missing.
    grouped_data = df.groupby(['producer_name', 'processor_name'])['dropoff_metered'].sum().fillna(0)

    for (dairy, handler), volume in grouped_data.items():
        volume_by_dairy_handler[dairy][handler] += volume

    return volume_by_dairy_handler

def display_results(volume_data, year, month):
    """
    Displays the aggregated volume data in a user-friendly format, including subtotals.
    """
    if not volume_data:
        print("No volume data to display.")
        return

    month_name = calendar.month_name[month]
    print(f"\n--- Monthly Volume Report for {month_name} {year} ---")

    grand_total = 0
    for dairy, handlers in sorted(volume_data.items()):
        print(f"\nDairy: {dairy}")
        dairy_total = sum(handlers.values())
        grand_total += dairy_total

        for handler, volume in sorted(handlers.items()):
            print(f"  -> Handler: {handler}, Total Volume: {int(volume):,}")
        
        print(f"  -----------------------------")
        print(f"  Total for {dairy}: {int(dairy_total):,}")

    print("\n=================================================")
    print(f"GRAND TOTAL FOR {month_name.upper()} {year}: {int(grand_total):,}")
    print("=================================================\n")

def main():
    """
    Main function to fetch and process milk movement data for a full month.
    """
    parser = argparse.ArgumentParser(
        description="Fetch and process milk movement data for a specific month."
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2025,
        help="The year to fetch data for (e.g., 2025)."
    )
    parser.add_argument(
        "--month",
        type=int,
        default=5,
        help="The month to fetch data for (e.g., 5 for May)."
    )
    args = parser.parse_args()
    year = args.year
    month = args.month
    month_name = calendar.month_name[month]

    print(f"Fetching data for {month_name} {year}...")

    all_summaries = []
    start_of_month = date(year, month, 1)
    num_days = calendar.monthrange(year, month)[1]
    end_of_month = date(year, month, num_days)

    current_start = start_of_month
    while current_start <= end_of_month:
        # Fetch in CHUNK_DAYS chunks to be safe
        current_end = current_start + timedelta(days=CHUNK_DAYS - 1)
        if current_end > end_of_month:
            current_end = end_of_month

        start_str = current_start.strftime("%Y-%m-%d")
        end_str = current_end.strftime("%Y-%m-%d")
        
        print(f"Fetching data from {start_str} to {end_str}...")

        summaries = get_load_summaries(start_str, end_str)
        if summaries is not None:
            all_summaries.extend(summaries)
        else:
             print(f"Could not fetch data for range {start_str} to {end_str}. Aborting.")
             return

        current_start += timedelta(days=CHUNK_DAYS)

    if all_summaries:
        print(f"\nSuccessfully fetched a total of {len(all_summaries):,} load summaries. Filtering and processing data...")
        volume_data = process_load_summaries(all_summaries)
        display_results(volume_data, year, month)
    else:
        print(f"No load summaries found for {month_name} {year}.")


if __name__ == "__main__":
    main() 