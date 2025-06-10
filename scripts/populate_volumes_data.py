#!/usr/bin/env python3
"""
Volumes Data Population Script
Runs the dairy volume logic and stores results in the database.
Should be run monthly via cron/scheduler.
"""

import sys
import os
import psycopg2
from datetime import datetime, date, timedelta
import calendar
import json
import pandas as pd
from collections import defaultdict

# Add parent directory to import our volume script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from get_dairy_volume import get_load_summaries, process_load_summaries

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "dairy_operations"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

def get_dairy_mapping(conn):
    """Fetches the dairy name mappings from the database."""
    mapping = {}
    with conn.cursor() as cur:
        # Fetch from milk_movement_names for volumes
        cur.execute("SELECT id, milk_movement_names FROM dairies")
        for row in cur.fetchall():
            dairy_id, names = row
            if names:
                for name in names:
                    mapping[name] = dairy_id
    return mapping

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def clear_old_pickup_logs(conn, report_month):
    """Clear old raw pickup logs for the target month before inserting new ones."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM pickup_logs WHERE report_month = %s", (report_month,))
        print(f"Cleared old pickup logs for {report_month.strftime('%Y-%m')}")

def populate_volumes_data(year=None, month=None):
    """Populate volumes data table from dairy volume logic"""
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month
    
    try:
        print(f"Starting volume data population for {year}-{month:02d}...")
        
        with get_db_connection() as conn:
            # Get the centralized dairy mapping
            dairy_name_mapping = get_dairy_mapping(conn)
            if not dairy_name_mapping:
                print("FATAL: Could not load dairy mappings from the database.")
                return

            # Calculate date range for the month
            start_of_month = date(year, month, 1)
            num_days = calendar.monthrange(year, month)[1]
            end_of_month = date(year, month, num_days)
            
            # Get all load summaries for the month (using existing chunking logic)
            all_summaries = []
            current_start = start_of_month
            CHUNK_DAYS = 7
            
            while current_start <= end_of_month:
                current_end = min(
                    current_start + timedelta(days=CHUNK_DAYS - 1),
                    end_of_month
                )
                
                start_str = current_start.strftime("%Y-%m-%d")
                end_str = current_end.strftime("%Y-%m-%d")
                
                print(f"Fetching data from {start_str} to {end_str}...")
                summaries = get_load_summaries(start_str, end_str)
                
                if summaries:
                    all_summaries.extend(summaries)
                
                current_start = current_end + timedelta(days=1)
            
            if not all_summaries:
                print(f"No load summaries found for {year}-{month:02d}")
                return
            
            print(f"Found {len(all_summaries)} total load summaries")
            
            df = pd.DataFrame(all_summaries)
            # Ensure required columns exist
            required_cols = ['hauler_number', 'producer_name', 'processor_name', 'dropoff_metered', 'invoice_number']
            if not all(col in df.columns for col in required_cols):
                print(f"Error: API data is missing required columns. Required: {required_cols}")
                return
            
            # Filter for specific hauler number
            HAULER_NUMBER = "77"
            df = df[df["hauler_number"] == HAULER_NUMBER].copy()
            
            if df.empty:
                print(f"No data found for hauler number {HAULER_NUMBER}")
                return

            # --- 1. Insert Raw Pickup Logs ---
            report_month_date = date(year, month, 1)
            clear_old_pickup_logs(conn, report_month_date)
            
            with conn.cursor() as cur:
                log_insert_count = 0
                for _, row in df.iterrows():
                    dairy_name = row.get('producer_name')
                    dairy_id = dairy_name_mapping.get(dairy_name)

                    if not dairy_id:
                        continue # Skip if no mapping found

                    # Coalesce trailer and truck numbers
                    trailer = row.get('trailer_number_1') or row.get('trailer_number_2') or 'N/A'
                    truck = row.get('truck_number') or 'N/A'
                    
                    # Safely handle dropoff weight, converting potential NaN to 0
                    dropoff_weight = row.get('dropoff_metered', 0)
                    if pd.isna(dropoff_weight):
                        dropoff_weight = 0
                    
                    # Parse pickup date, fallback to report month start
                    try:
                        pickup_date = datetime.fromisoformat(row.get('dropoff_date')) if pd.notna(row.get('dropoff_date')) else report_month_date
                    except (TypeError, ValueError):
                        pickup_date = report_month_date

                    cur.execute("""
                        INSERT INTO pickup_logs
                        (dairy_id, report_month, pickup_date, driver_name, invoice_number, route_number, handler_name, dropoff_weight, trailer_number, truck_number)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (dairy_id, report_month, invoice_number) DO NOTHING
                    """, (
                        dairy_id,
                        report_month_date,
                        pickup_date,
                        row.get('driver_name', 'N/A'),
                        row.get('invoice_number', 'N/A'),
                        row.get('route_number', 'N/A'),
                        row.get('processor_name', 'N/A'),
                        int(dropoff_weight),
                        trailer,
                        truck
                    ))
                    log_insert_count += 1
                print(f"Inserted {log_insert_count} raw pickup logs.")

            # --- 2. Process and Insert Aggregated Volume Data ---
            print("Processing summaries with direct mapping logic...")
            volume_by_dairy_handler = defaultdict(dict)
            
            # Group by dairy and handler, get sum of volume and count of pickups
            grouped_data = df.groupby(['producer_name', 'processor_name'])['dropoff_metered'].agg(['sum', 'count']).reset_index()
            
            # Apply our mapping
            for _, row in grouped_data.iterrows():
                dairy_name = row['producer_name']
                handler_name = row['processor_name']
                volume = row['sum']
                count = row['count']
                
                if dairy_name in dairy_name_mapping:
                    mapped_dairy_id = dairy_name_mapping[dairy_name]
                    # Store as a tuple of (volume, count)
                    current_vol, current_count = volume_by_dairy_handler[mapped_dairy_id].get(handler_name, (0, 0))
                    volume_by_dairy_handler[mapped_dairy_id][handler_name] = (current_vol + volume, current_count + count)
                    print(f"Mapped: {dairy_name} -> {mapped_dairy_id}: {volume:,.0f} lbs, {count} pickups")
                else:
                    print(f"Warning: No mapping found for dairy '{dairy_name}' - SKIPPING")
            
            # Insert new aggregated volume data
            with conn.cursor() as cur:
                insert_count = 0
                
                for dairy_id, handlers in volume_by_dairy_handler.items():
                    for handler_name, (total_volume, total_pickups) in handlers.items():
                        # Convert to integer pounds
                        total_volume_lbs = int(total_volume)
                        pickup_count = int(total_pickups)
                        
                        # Insert volume data
                        cur.execute("""
                            INSERT INTO volumes_data 
                            (dairy_id, report_month, handler_name, total_volume_lbs, pickup_count, last_updated)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (dairy_id, report_month, handler_name) 
                            DO UPDATE SET 
                                total_volume_lbs = EXCLUDED.total_volume_lbs,
                                pickup_count = EXCLUDED.pickup_count,
                                last_updated = EXCLUDED.last_updated
                        """, (
                            dairy_id,
                            report_month_date,
                            handler_name,
                            total_volume_lbs,
                            pickup_count,
                            datetime.utcnow()
                        ))
                        insert_count += 1
                        
                        print(f"Inserted: {dairy_id} -> {handler_name}: {total_volume_lbs:,} lbs, {pickup_count} pickups")
                
                conn.commit()
                print(f"Successfully inserted/updated {insert_count} aggregated volume records for {year}-{month:02d}")
        
    except Exception as e:
        print(f"Error populating volume data: {str(e)}")
        raise

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Populate volume data for a specific month")
    parser.add_argument("--year", type=int, help="Year (default: current year)")
    parser.add_argument("--month", type=int, help="Month (default: current month)")
    args = parser.parse_args()
    
    populate_volumes_data(args.year, args.month) 