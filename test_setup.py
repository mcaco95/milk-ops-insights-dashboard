#!/usr/bin/env python3
"""
Test script to verify the database-driven setup works correctly
"""

import os
import sys
import psycopg2
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "dairy_operations"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "31012662")
}

def test_database_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()
            print(f"✅ Database connection successful: {version[0]}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def test_tables_exist():
    """Test that required tables exist"""
    tables = ['dairies', 'users', 'tanks_data', 'routes_data', 'volumes_data']
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            for table in tables:
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = %s
                    )
                """, (table,))
                exists = cur.fetchone()[0]
                if exists:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' missing")
                    return False
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking tables: {str(e)}")
        return False

def test_sample_data():
    """Test that sample data exists"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            # Check dairies
            cur.execute("SELECT COUNT(*) FROM dairies")
            dairy_count = cur.fetchone()[0]
            print(f"✅ Found {dairy_count} dairies in database")
            
            # Check users
            cur.execute("SELECT COUNT(*) FROM users")
            user_count = cur.fetchone()[0]
            print(f"✅ Found {user_count} users in database")
            
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error checking sample data: {str(e)}")
        return False

def insert_test_data():
    """Insert some test data to verify the population scripts would work"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            # Insert test tank data
            cur.execute("""
                INSERT INTO tanks_data 
                (dairy_id, barn_name, tank_name, current_volume_lbs, capacity_lbs, is_milking, is_washing, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (dairy_id, barn_name, tank_name) 
                DO UPDATE SET 
                    current_volume_lbs = EXCLUDED.current_volume_lbs,
                    last_updated = EXCLUDED.last_updated
            """, (
                "milky_way_dairy",
                "North Barn",
                "Tank 1",
                85000,
                110000,
                False,
                False,
                datetime.utcnow()
            ))
            
            # Insert test route data
            cur.execute("""
                INSERT INTO routes_data 
                (dairy_id, samsara_route_id, report_date, driver_name, truck_id, status, target_location, last_updated)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (dairy_id, report_date, samsara_route_id, driver_name, truck_id) 
                DO UPDATE SET 
                    status = EXCLUDED.status,
                    last_updated = EXCLUDED.last_updated
            """, (
                "milky_way_dairy",
                "test_route_1",
                datetime.now().date(),
                "John Doe",
                "DMT 123",
                "active",
                "Milky Way North Barn",
                datetime.utcnow()
            ))
            
            # Insert test volume data
            cur.execute("""
                INSERT INTO volumes_data 
                (dairy_id, report_month, handler_name, total_volume_lbs, last_updated)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (dairy_id, report_month, handler_name) 
                DO UPDATE SET 
                    total_volume_lbs = EXCLUDED.total_volume_lbs,
                    last_updated = EXCLUDED.last_updated
            """, (
                "milky_way_dairy",
                datetime.now().date().replace(day=1),
                "Fairlife LLC",
                1250000,
                datetime.utcnow()
            ))
            
            conn.commit()
            print("✅ Test data inserted successfully")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Error inserting test data: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Database-Driven Dairy Operations Setup")
    print("=" * 50)
    
    success = True
    
    # Test database connection
    if not test_database_connection():
        success = False
    
    # Test tables exist
    if not test_tables_exist():
        success = False
    
    # Test sample data
    if not test_sample_data():
        success = False
    
    # Insert test data
    if not insert_test_data():
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! The setup is working correctly.")
        print("\nNext steps:")
        print("1. Run the scheduler: python scripts/scheduler.py")
        print("2. Start the backend: cd backend && uvicorn app.main:app --reload")
        print("3. Start the frontend: cd milk-ops-insights-dashboard && npm start")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 