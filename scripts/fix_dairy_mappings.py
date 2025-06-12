#!/usr/bin/env python3
"""
Fix Dairy Mappings Script

This script ensures that the three troubled dairies have correct mappings
in the database so that populate_tanks_data.py can find them.

Should run BEFORE populate_tanks_data.py in the scheduler.
"""

import sys
import os
import psycopg2
from datetime import datetime

# Add parent directory to import our tank level script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.populate_tanks_data import get_db_connection

def fix_dairy_mappings():
    """Ensures the troubled dairies have correct mappings in the database."""
    print("🔧 FIXING DAIRY MAPPINGS")
    print("=" * 50)
    
    # The mappings we know are correct from form data
    correct_mappings = {
        "az_dairy": ["Arizona Dairy", "AZ Dairy"],
        "d_i_dairy": ["D&I Coolidge (805)", "D&I Dairy"],
        "d_i_holsteins": ["D&I Stanfield (716)", "D & I Holsteins"]
    }
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                for dairy_id, names in correct_mappings.items():
                    print(f"\n📝 Processing {dairy_id}...")
                    
                    # Check if the dairy exists
                    cur.execute("SELECT id, tank_dashboard_names FROM dairies WHERE id = %s", (dairy_id,))
                    result = cur.fetchone()
                    
                    if result:
                        current_names = result[1]
                        print(f"   Current tank_dashboard_names: {current_names}")
                        
                        # Update the tank_dashboard_names field with our correct mapping
                        cur.execute("""
                            UPDATE dairies 
                            SET tank_dashboard_names = %s 
                            WHERE id = %s
                        """, (names, dairy_id))
                        
                        print(f"   ✅ Updated tank_dashboard_names to: {names}")
                        
                    else:
                        print(f"   ❌ Dairy {dairy_id} not found in database!")
                        
                        # Create the dairy record if it doesn't exist
                        cur.execute("""
                            INSERT INTO dairies (id, tank_dashboard_names) 
                            VALUES (%s, %s)
                        """, (dairy_id, names))
                        
                        print(f"   ✅ Created new dairy record with names: {names}")
                
                conn.commit()
                print(f"\n✅ MAPPINGS FIXED SUCCESSFULLY")
                
                # Verify the mappings work
                print(f"\n🔍 VERIFYING MAPPINGS...")
                cur.execute("SELECT id, tank_dashboard_names FROM dairies WHERE id IN %s", 
                           (tuple(correct_mappings.keys()),))
                
                for row in cur.fetchall():
                    dairy_id, names = row
                    print(f"   {dairy_id}: {names}")
                
    except Exception as e:
        print(f"❌ ERROR FIXING MAPPINGS: {str(e)}")
        raise

if __name__ == "__main__":
    fix_dairy_mappings() 