#!/usr/bin/env python3
"""
Fix Troubled Dairies Script

This script runs with the scheduler and specifically handles the 3 dairies
that aren't working with the main populate_tanks_data.py script.

Runs AFTER populate_tanks_data.py to fix the missing data.
"""

import sys
import os
import psycopg2
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tank_level_dashboard import get_volume_submissions, parse_submission_volumes, calculate_tank_status
from scripts.populate_tanks_data import get_db_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - FIX_TROUBLED_DAIRIES - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_troubled_dairies():
    """Fix tank data for the 3 troubled dairies."""
    logger.info("🔧 STARTING FIX TROUBLED DAIRIES SCRIPT")
    logger.info("=" * 50)
    
    # The exact 3 dairies that are failing
    troubled_mappings = {
        "Arizona Dairy": "az_dairy",
        "D&I Coolidge (805)": "d_i_dairy", 
        "D&I Stanfield (716)": "d_i_holsteins"
    }
    
    logger.info(f"Target dairies: {list(troubled_mappings.keys())}")
    
    try:
        # Get form submissions and calculate tank status
        logger.info("Getting form submissions...")
        submissions = get_volume_submissions(hours_back=48)
        logger.info(f"Found {len(submissions)} form submissions")
        
        logger.info("Parsing submissions...")
        current_data = []
        for submission in submissions:
            parsed = parse_submission_volumes(submission)
            if parsed.get('dairy') and parsed.get('volumes'):
                current_data.append(parsed)
        
        logger.info(f"Parsed {len(current_data)} submissions with dairy and volume data")
        
        # Check if troubled dairies have raw form data
        troubled_data = {}
        for dairy_name in troubled_mappings.keys():
            matching_submissions = [item for item in current_data if item['dairy'] == dairy_name]
            logger.info(f"Raw data for {dairy_name}: {len(matching_submissions)} submissions")
            if matching_submissions:
                troubled_data[dairy_name] = matching_submissions
                # Show latest volumes
                latest = max(matching_submissions, key=lambda x: x.get('timestamp', ''))
                logger.info(f"  Latest volumes: {latest['volumes']}")
        
        # Calculate tank statuses for verification
        logger.info("Calculating tank statuses for verification...")
        tank_statuses = calculate_tank_status(current_data)
        logger.info(f"Tank statuses calculated for {len(tank_statuses)} dairies")
        
        # Process only the troubled dairies using raw form data
        with get_db_connection() as conn:
            logger.info("Connected to database successfully")
            with conn.cursor() as cur:
                fixed_count = 0
                
                for dairy_name, dairy_id in troubled_mappings.items():
                    if dairy_name not in troubled_data:
                        logger.warning(f"⚠️  {dairy_name}: No raw form data, skipping")
                        continue
                    
                    logger.info(f"🏭 Processing {dairy_name} -> {dairy_id}")
                    submissions = troubled_data[dairy_name]
                    barn_name = "Main Barn"  # All 3 use Main Barn
                    
                    # Get the latest submission for each tank
                    latest_by_tank = {}
                    for submission in submissions:
                        for tank_name, volume in submission['volumes'].items():
                            if tank_name not in latest_by_tank or submission.get('timestamp', '') > latest_by_tank[tank_name].get('timestamp', ''):
                                latest_by_tank[tank_name] = {
                                    'volume': volume,
                                    'timestamp': submission.get('timestamp', ''),
                                    'is_milking': submission.get('milking_tank') == tank_name
                                }
                    
                    logger.info(f"  Found latest data for {len(latest_by_tank)} tanks")
                    
                    for tank_name, tank_data in latest_by_tank.items():
                        current_volume = tank_data['volume'] or 0
                        timestamp_str = tank_data['timestamp']
                        is_milking = tank_data['is_milking']
                        
                        # Only process tanks with actual volume data OR if it's a milking tank
                        if current_volume > 0 or is_milking:
                            logger.info(f"  📦 {tank_name}: {current_volume} lbs (milking: {is_milking}) - FORCE UPDATING")
                            
                            # Set basic tank info
                            base_volume = current_volume  # Use current as base for now
                            predicted_added = 0  # No prediction for fix script
                            
                            # Get capacity based on dairy
                            if dairy_id == "az_dairy":
                                capacity = 160000
                            elif dairy_id == "d_i_dairy":
                                capacity = 100000
                            elif dairy_id == "d_i_holsteins":
                                capacity = 66000
                            else:
                                capacity = 100000  # default
                            
                            time_to_full = None
                            last_pulled_at = datetime.fromisoformat(timestamp_str) if timestamp_str else None
                            
                            # Wash status logic
                            cur.execute(
                                "SELECT current_volume_lbs, wash_started_at FROM tanks_data WHERE dairy_id = %s AND tank_name = %s",
                                (dairy_id, tank_name)
                            )
                            result = cur.fetchone()
                            
                            previous_volume = result[0] if result else 0
                            existing_wash_started_at = result[1] if result else None
                            new_wash_started_at = existing_wash_started_at
                            
                            if current_volume < 5000 and previous_volume >= 5000:
                                new_wash_started_at = datetime.utcnow()
                                logger.info(f"    Wash cycle detected for {tank_name}")
                            
                            is_washing = new_wash_started_at is not None
                            
                            # Force update the tank data
                            logger.info(f"    Executing FORCE database update for {dairy_id}.{tank_name}")
                            cur.execute("""
                                INSERT INTO tanks_data 
                                (dairy_id, barn_name, tank_name, current_volume_lbs, base_volume_lbs, predicted_added_lbs, capacity_lbs, time_to_full_hours, is_milking, is_washing, last_pulled_at, wash_started_at, last_updated)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                ON CONFLICT (dairy_id, barn_name, tank_name) 
                                DO UPDATE SET 
                                    current_volume_lbs = EXCLUDED.current_volume_lbs,
                                    base_volume_lbs = EXCLUDED.base_volume_lbs,
                                    predicted_added_lbs = EXCLUDED.predicted_added_lbs,
                                    capacity_lbs = EXCLUDED.capacity_lbs,
                                    time_to_full_hours = EXCLUDED.time_to_full_hours,
                                    is_milking = EXCLUDED.is_milking,
                                    is_washing = EXCLUDED.is_washing,
                                    last_pulled_at = EXCLUDED.last_pulled_at,
                                    wash_started_at = EXCLUDED.wash_started_at,
                                    last_updated = EXCLUDED.last_updated
                            """, (
                                dairy_id, barn_name, tank_name, current_volume, base_volume,
                                predicted_added, capacity, time_to_full, is_milking, is_washing,
                                last_pulled_at, new_wash_started_at, datetime.utcnow()
                            ))
                            
                            fixed_count += 1
                            logger.info(f"    ✅ Successfully FORCE updated {tank_name} with {current_volume} lbs")
                        else:
                            logger.info(f"  ⚪ {tank_name}: {current_volume} lbs (not milking, skipping)")
                
                logger.info("Committing database changes...")
                conn.commit()
                logger.info(f"✅ SUCCESSFULLY FIXED {fixed_count} tank records for troubled dairies")
                
                if fixed_count == 0:
                    logger.warning("⚠️  NO TANKS WERE UPDATED - All tanks had 0 volume and weren't milking")
                else:
                    logger.info("🎉 TROUBLED DAIRIES SHOULD NOW HAVE CORRECT DATA!")
                
    except Exception as e:
        logger.error(f"❌ ERROR in fix_troubled_dairies: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        raise

if __name__ == "__main__":
    fix_troubled_dairies() 