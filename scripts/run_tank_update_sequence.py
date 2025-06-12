#!/usr/bin/env python3
"""
Tank Update Sequence Script

This script runs the complete tank update sequence:
1. Populate tanks data (main script)
2. Fix troubled dairies (targeted fix for the 3 failing dairies)

This should be the script called by the scheduler.
"""

import sys
import os
from datetime import datetime
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - TANK_UPDATE_SEQUENCE - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_tank_update_sequence():
    """Runs the complete tank update sequence."""
    logger.info("🚀 STARTING TANK UPDATE SEQUENCE")
    logger.info("=" * 60)
    logger.info(f"Started at: {datetime.now()}")
    
    success = True
    step1_success = False
    step2_success = False
    
    try:
        # Step 1: Run main populate tanks script
        logger.info("\n" + "="*60)
        logger.info("STEP 1: POPULATING TANKS DATA (MAIN SCRIPT)")
        logger.info("="*60)
        
        logger.info("Importing and running populate_tanks_data...")
        from scripts.populate_tanks_data import populate_tanks_data
        populate_tanks_data()
        step1_success = True
        logger.info("✅ Step 1 completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Step 1 failed: {str(e)}")
        logger.error("Step 1 traceback:", exc_info=True)
        success = False
    
    try:
        # Step 2: Fix troubled dairies
        logger.info("\n" + "="*60)
        logger.info("STEP 2: FIXING TROUBLED DAIRIES")
        logger.info("="*60)
        
        logger.info("Importing and running fix_troubled_dairies...")
        from scripts.fix_troubled_dairies import fix_troubled_dairies
        fix_troubled_dairies()
        step2_success = True
        logger.info("✅ Step 2 completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Step 2 failed: {str(e)}")
        logger.error("Step 2 traceback:", exc_info=True)
        success = False
    
    # Final status
    logger.info("\n" + "="*60)
    logger.info("SEQUENCE COMPLETE")
    logger.info("="*60)
    logger.info(f"Finished at: {datetime.now()}")
    
    # Detailed status report
    logger.info(f"Step 1 (Main Script): {'✅ SUCCESS' if step1_success else '❌ FAILED'}")
    logger.info(f"Step 2 (Fix Troubled): {'✅ SUCCESS' if step2_success else '❌ FAILED'}")
    
    if success:
        logger.info("🎉 ALL STEPS COMPLETED SUCCESSFULLY")
        logger.info("The troubled dairies (Arizona Dairy, D&I Coolidge, D&I Stanfield)")
        logger.info("should now have their tank data properly updated.")
        
        # Log a verification query suggestion
        logger.info("To verify results, run:")
        logger.info("docker exec -it dairymen-postgres-1 psql -U postgres -d dairy_operations -c \"SELECT dairy_id, tank_name, current_volume_lbs, last_updated FROM tanks_data WHERE dairy_id IN ('az_dairy', 'd_i_dairy', 'd_i_holsteins') ORDER BY dairy_id, tank_name;\"")
        
    else:
        logger.warning("⚠️  SOME STEPS FAILED - CHECK LOGS ABOVE")
        
        if not step1_success and not step2_success:
            logger.error("💥 BOTH STEPS FAILED - CRITICAL ISSUE")
        elif not step1_success:
            logger.warning("⚠️  Main script failed but fix script may have worked")
        elif not step2_success:
            logger.warning("⚠️  Main script worked but fix script failed")
        
    return success

if __name__ == "__main__":
    logger.info("Script called directly - starting execution")
    success = run_tank_update_sequence()
    exit_code = 0 if success else 1
    logger.info(f"Exiting with code: {exit_code}")
    sys.exit(exit_code) 