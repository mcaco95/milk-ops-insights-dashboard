#!/usr/bin/env python3
"""
Data Population Scheduler
Runs the data population scripts at appropriate intervals:
- Tank data: Every 10 minutes
- Route data: Every 15 minutes (INCREASED FREQUENCY for real-time tracking)
- Volume data: Daily (and monthly for new months)
"""

import schedule
import time
import logging
import subprocess
import sys
import os
from datetime import datetime, date, timedelta
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/dairy_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Script paths
SCRIPT_DIR = Path(__file__).parent
TANK_SCRIPT = SCRIPT_DIR / "populate_tanks_data.py"
ROUTES_SCRIPT = SCRIPT_DIR / "populate_routes_data.py"  # THIS NOW USES THE NEW WORKING LOGIC!
VOLUMES_SCRIPT = SCRIPT_DIR / "populate_volumes_data.py"

def run_script(script_path, args=None):
    """Run a Python script with optional arguments"""
    try:
        cmd = [sys.executable, str(script_path)]
        if args:
            cmd.extend(args)
        
        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # Increased timeout to 10 minutes
        
        if result.returncode == 0:
            logger.info(f"Success: {script_path.name}")
            if result.stdout:
                logger.info(f"Output: {result.stdout.strip()}")
        else:
            logger.error(f"Failed: {script_path.name} - Return code: {result.returncode}")
            if result.stderr:
                logger.error(f"Error: {result.stderr.strip()}")
                
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout: {script_path.name} took longer than 10 minutes")
    except Exception as e:
        logger.error(f"Exception running {script_path.name}: {str(e)}")

def populate_tank_data():
    """Populate tank data - runs every 10 minutes"""
    logger.info("Starting tank data population...")
    run_script(TANK_SCRIPT)

def populate_route_data():
    """Populate route data for today - runs every 3 minutes for REAL-TIME tracking"""
    logger.info("Starting REAL-TIME route data population (using proven debug logic)...")
    run_script(ROUTES_SCRIPT)

def populate_volume_data():
    """Populate volume data for current month - runs daily"""
    logger.info("Starting volume data population...")
    run_script(VOLUMES_SCRIPT)

def populate_historical_routes():
    """Populate route data for yesterday (to catch any late updates) - runs daily"""
    yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
    logger.info(f"Starting historical route data population for {yesterday}...")
    run_script(ROUTES_SCRIPT, ["--date", yesterday])

def populate_historical_volumes():
    """Populate volume data for previous month (if it's early in the month) - runs weekly"""
    today = date.today()
    if today.day <= 7:  # Only run for first week of month
        last_month = today.replace(day=1) - timedelta(days=1)
        logger.info(f"Starting historical volume data population for {last_month.year}-{last_month.month:02d}...")
        run_script(VOLUMES_SCRIPT, ["--year", str(last_month.year), "--month", str(last_month.month)])

def setup_schedule():
    """Setup the schedule for all data population tasks"""
    logger.info("Setting up data population schedule...")
    
    # Tank data - every 10 minutes
    schedule.every(10).minutes.do(populate_tank_data)
    
    # Route data - EVERY 3 MINUTES for real-time tracking (using new working script!)
    schedule.every(3).minutes.do(populate_route_data)
    
    # Volume data - daily at 2 AM
    schedule.every().day.at("02:00").do(populate_volume_data)
    
    # Historical route data - daily at 3 AM
    schedule.every().day.at("03:00").do(populate_historical_routes)
    
    # Historical volume data - weekly on Monday at 4 AM
    schedule.every().monday.at("04:00").do(populate_historical_volumes)
    
    logger.info("Schedule setup complete:")
    logger.info("- Tank data: Every 10 minutes")
    logger.info("- Route data: Every 3 minutes (REAL-TIME with proven debug logic!)")
    logger.info("- Volume data: Daily at 2:00 AM")
    logger.info("- Historical routes: Daily at 3:00 AM")
    logger.info("- Historical volumes: Weekly (Monday) at 4:00 AM")

def run_initial_population():
    """Run initial data population on startup"""
    logger.info("Running initial data population...")
    
    # Run all scripts once to populate initial data
    populate_tank_data()
    time.sleep(5)  # Small delay between scripts
    
    populate_route_data()
    time.sleep(5)
    
    populate_volume_data()
    
    logger.info("Initial data population complete")

def main():
    """Main scheduler loop"""
    logger.info("Starting Data Population Scheduler with NEW WORKING ROUTES LOGIC...")
    
    # Run initial population
    run_initial_population()
    
    # Setup schedule
    setup_schedule()
    
    # Main loop
    logger.info("Scheduler is running. Press Ctrl+C to stop.")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
        raise

if __name__ == "__main__":
    main() 