#!/usr/bin/env python3
"""
Historical Data Population Script
Safely populates all available historical data with rate limiting and progress tracking.
This script can be run manually to backfill data without breaking the system.
"""

import sys
import os
import time
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path

# Add parent directory to import our populate scripts
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from populate_volumes_data import populate_volumes_data
from populate_routes_data import populate_routes_data

def safe_populate_volumes_history(start_year=2023, end_year=None, delay_seconds=5):
    """
    Safely populate volume data for all months from start_year to end_year
    """
    if end_year is None:
        end_year = datetime.now().year
    
    print(f"🚀 Starting HISTORICAL VOLUMES population from {start_year} to {end_year}")
    print(f"⏱️  Using {delay_seconds}s delay between months to avoid rate limits")
    
    success_count = 0
    error_count = 0
    
    for year in range(start_year, end_year + 1):
        end_month = 12 if year < end_year else datetime.now().month
        
        for month in range(1, end_month + 1):
            try:
                print(f"\n📊 Processing {year}-{month:02d}...")
                populate_volumes_data(year, month)
                success_count += 1
                print(f"✅ Success: {year}-{month:02d}")
                
                # Rate limiting delay (except for last iteration)
                if not (year == end_year and month == end_month):
                    print(f"⏳ Waiting {delay_seconds}s before next month...")
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                error_count += 1
                print(f"❌ Error in {year}-{month:02d}: {str(e)}")
                print(f"⏭️  Continuing to next month...")
                time.sleep(2)  # Brief pause before continuing
    
    print(f"\n🎯 HISTORICAL VOLUMES COMPLETE!")
    print(f"✅ Successful months: {success_count}")
    print(f"❌ Failed months: {error_count}")
    return success_count, error_count

def safe_populate_routes_history(start_date, end_date=None, delay_seconds=2):
    """
    Safely populate route data for all days from start_date to end_date
    """
    if end_date is None:
        end_date = date.today() - timedelta(days=1)  # Yesterday
    
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    print(f"🚀 Starting HISTORICAL ROUTES population from {start_date} to {end_date}")
    print(f"⏱️  Using {delay_seconds}s delay between days to avoid rate limits")
    
    success_count = 0
    error_count = 0
    current_date = start_date
    
    while current_date <= end_date:
        try:
            print(f"\n🚛 Processing {current_date}...")
            populate_routes_data(current_date)
            success_count += 1
            print(f"✅ Success: {current_date}")
            
            # Rate limiting delay (except for last iteration)
            if current_date < end_date:
                print(f"⏳ Waiting {delay_seconds}s before next day...")
                time.sleep(delay_seconds)
                
        except Exception as e:
            error_count += 1
            print(f"❌ Error in {current_date}: {str(e)}")
            print(f"⏭️  Continuing to next day...")
            time.sleep(1)  # Brief pause before continuing
        
        current_date += timedelta(days=1)
    
    print(f"\n🎯 HISTORICAL ROUTES COMPLETE!")
    print(f"✅ Successful days: {success_count}")
    print(f"❌ Failed days: {error_count}")
    return success_count, error_count

def main():
    parser = argparse.ArgumentParser(description="Populate historical data safely")
    parser.add_argument("--volumes", action="store_true", help="Populate historical volumes")
    parser.add_argument("--routes", action="store_true", help="Populate historical routes")
    parser.add_argument("--all", action="store_true", help="Populate all historical data")
    
    # Volume options
    parser.add_argument("--start-year", type=int, default=2023, help="Start year for volumes (default: 2023)")
    parser.add_argument("--end-year", type=int, help="End year for volumes (default: current year)")
    
    # Route options  
    parser.add_argument("--start-date", type=str, help="Start date for routes (YYYY-MM-DD, default: 30 days ago)")
    parser.add_argument("--end-date", type=str, help="End date for routes (YYYY-MM-DD, default: yesterday)")
    
    # Rate limiting
    parser.add_argument("--volume-delay", type=int, default=5, help="Delay between volume months (default: 5s)")
    parser.add_argument("--route-delay", type=int, default=2, help="Delay between route days (default: 2s)")
    
    args = parser.parse_args()
    
    if not (args.volumes or args.routes or args.all):
        print("Please specify --volumes, --routes, or --all")
        parser.print_help()
        return
    
    print("🏛️  DAIRY OPERATIONS HISTORICAL DATA POPULATION")
    print("=" * 50)
    
    # Populate volumes if requested
    if args.volumes or args.all:
        print(f"\n📊 VOLUMES: Populating from {args.start_year} to {args.end_year or 'current year'}")
        vol_success, vol_errors = safe_populate_volumes_history(
            start_year=args.start_year,
            end_year=args.end_year,
            delay_seconds=args.volume_delay
        )
        
        if args.all:
            print(f"\n⏸️  Pausing 10 seconds before routes...")
            time.sleep(10)
    
    # Populate routes if requested
    if args.routes or args.all:
        start_date = args.start_date or (date.today() - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = args.end_date or (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        print(f"\n🚛 ROUTES: Populating from {start_date} to {end_date}")
        route_success, route_errors = safe_populate_routes_history(
            start_date=start_date,
            end_date=end_date,
            delay_seconds=args.route_delay
        )
    
    print(f"\n🎉 HISTORICAL DATA POPULATION COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    main() 