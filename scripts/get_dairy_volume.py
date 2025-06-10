import requests
import os
import argparse
import pandas as pd
from datetime import date, timedelta
import calendar
import psycopg2
from psycopg2.extras import execute_values

# --- Configuration ---
MILK_MOOVEMENT_API_TOKEN = os.getenv("MILK_MOOVEMENT_API_TOKEN", "amlvr8mXyI14JPu9g4kY69I10gTvc5iW4f5MNWcM")
API_BASE_URL = "https://api.prod.milkmoovement.io/v1"
HAULER_NUMBER = "77"
CHUNK_DAYS = 7
DB_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dairydb")

# --- Database Functions ---
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        return None

def get_dairy_id_map(conn):
    """Fetches a map of milk_movement_names to dairy_id."""
    with conn.cursor() as cur:
        cur.execute("SELECT id, milk_movement_names FROM dairies")
        dairy_map = {}
        for row in cur.fetchall():
            dairy_id, names = row
            if names:
                for name in names:
                    # Normalize name for better matching
                    normalized = name.lower().replace(' ', '').replace('[', '').replace(']', '').replace('&', '').replace('(', '').replace(')', '').replace('dairy', '')
                    dairy_map[normalized] = dairy_id
        return dairy_map

def upsert_volume_data(conn, volume_data, report_month):
    """
    Inserts or updates volume data in the volumes_data table.
    """
    if not volume_data:
        print("No volume data to upsert.")
        return 0

    # Prepare data for execute_values
    # (dairy_id, report_month, handler_name, total_volume_lbs)
    first_day_of_month = date(report_month.year, report_month.month, 1)
    
    data_to_upsert = [
        (item['dairy_id'], first_day_of_month, item['handler'], item['volume'])
        for item in volume_data
    ]

    query = """
    INSERT INTO volumes_data (dairy_id, report_month, handler_name, total_volume_lbs)
    VALUES %s
    ON CONFLICT (dairy_id, report_month, handler_name)
    DO UPDATE SET
        total_volume_lbs = EXCLUDED.total_volume_lbs,
        last_updated = NOW() AT TIME ZONE 'UTC';
    """
    
    with conn.cursor() as cur:
        execute_values(cur, query, data_to_upsert, template=None, page_size=100)
        conn.commit()
        return cur.rowcount

# --- API & Data Processing Functions (some updated) ---
def get_load_summaries(start_date, end_date):
    """Fetches load summary data from the Milk Moovement API."""
    url = f"{API_BASE_URL}/pickups/load-summary"
    params = {"start_date": start_date, "end_date": end_date}
    headers = {"X-API-KEY": MILK_MOOVEMENT_API_TOKEN}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching load summaries for {start_date} to {end_date}: {e}")
        return None

def process_load_summaries(summaries, dairy_id_map):
    """
    Processes load summaries to calculate total volume per dairy handler
    and maps it to our internal dairy_id.
    """
    if not summaries:
        return []

    df = pd.DataFrame(summaries)
    required_cols = ['hauler_number', 'producer_name', 'processor_name', 'dropoff_metered']
    if not all(col in df.columns for col in required_cols):
        print("Error: API data is missing required columns. Cannot process.")
        return []

    df = df[df["hauler_number"] == HAULER_NUMBER]
    if df.empty:
        return []

    grouped = df.groupby(['producer_name', 'processor_name'])['dropoff_metered'].sum().reset_index()
    
    processed_data = []
    for _, row in grouped.iterrows():
        producer_name = row['producer_name']
        # Normalize producer name to match keys in dairy_id_map
        normalized_producer = producer_name.lower().replace(' ', '').replace('[', '').replace(']', '').replace('&', '').replace('(', '').replace(')', '').replace('dairy', '')
        
        dairy_id = dairy_id_map.get(normalized_producer)
        
        if dairy_id:
            processed_data.append({
                'dairy_id': dairy_id,
                'handler': row['processor_name'],
                'volume': row['dropoff_metered']
            })
        else:
            print(f"Warning: Could not find a matching dairy_id for producer '{producer_name}'. Skipping.")
            
    return processed_data

def main():
    """Main function to fetch, process, and store milk movement data."""
    parser = argparse.ArgumentParser(description="Fetch and store milk movement data.")
    parser.add_argument("--year", type=int, default=date.today().year)
    parser.add_argument("--month", type=int, default=date.today().month)
    args = parser.parse_args()

    year, month = args.year, args.month
    month_name = calendar.month_name[month]
    print(f"--- Starting Volume Ingestion for {month_name} {year} ---")
    
    conn = get_db_connection()
    if not conn:
        return

    try:
        dairy_id_map = get_dairy_id_map(conn)
        if not dairy_id_map:
            print("Error: Could not retrieve dairy mapping from database. Aborting.")
            return

        print(f"Found {len(dairy_id_map)} dairy name mappings in the database.")

        start_of_month = date(year, month, 1)
        num_days = calendar.monthrange(year, month)[1]
        end_of_month = date(year, month, num_days)

        all_summaries = []
        current_start = start_of_month
        while current_start <= end_of_month:
            current_end = current_start + timedelta(days=CHUNK_DAYS - 1)
            if current_end > end_of_month:
                current_end = end_of_month

            start_str, end_str = current_start.strftime("%Y-%m-%d"), current_end.strftime("%Y-%m-%d")
            print(f"Fetching data from {start_str} to {end_str}...")
            
            summaries = get_load_summaries(start_str, end_str)
            if summaries:
                all_summaries.extend(summaries)
            else:
                print(f"Could not fetch data for range {start_str} to {end_str}. May continue with partial data.")

            current_start += timedelta(days=CHUNK_DAYS)
        
        if not all_summaries:
            print(f"No load summaries found for {month_name} {year}.")
            return

        print(f"Successfully fetched a total of {len(all_summaries):,} load summaries. Processing...")
        volume_data = process_load_summaries(all_summaries, dairy_id_map)
        
        print(f"Processed {len(volume_data)} records to be upserted.")
        rows_affected = upsert_volume_data(conn, volume_data, start_of_month)
        
        print(f"--- Volume Ingestion Complete ---")
        print(f"{rows_affected} records were inserted or updated in the database.")

    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main() 