#!/usr/bin/env python3

import psycopg2
import os

# Database configuration (Docker environment) - same as populate_routes_data.py
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "postgres"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "dairy_operations"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

def normalize_dairy_name_my_function(dairy_name):
    """My normalize function"""
    if not dairy_name:
        return dairy_name
    
    # SPECIAL CASE: Any dairy starting with "T&K" should normalize to just "tk"
    if dairy_name.upper().startswith('T&K'):
        return 'tk'
    
    # Handle "Dickman (815)" variations - normalize to match database exactly
    dairy_upper = dairy_name.upper()
    if 'DICKMAN' in dairy_upper and '815' in dairy_upper:
        return 'dickmanandson815'  # What I think should match
    
    # Use the EXACT same normalization as get_dairy_volume.py (which works!)
    normalized = dairy_name.lower().replace(' ', '').replace('[', '').replace(']', '').replace('&', '').replace('(', '').replace(')', '').replace('dairy', '')
    return normalized

def normalize_dairy_name_database(dairy_name):
    """Database normalize function"""
    normalized = dairy_name.lower().replace(' ', '').replace('[', '').replace(']', '').replace('&', '').replace('(', '').replace(')', '').replace('dairy', '')
    return normalized

print("=== DICKMAN DAIRY DEBUG ===")
print(f"DB_CONFIG: {DB_CONFIG}")

conn = psycopg2.connect(**DB_CONFIG)
with conn.cursor() as cur:
    cur.execute("SELECT id, milk_movement_names FROM dairies WHERE id = 'dickman'")
    row = cur.fetchone()
    
    if row:
        dairy_id, names = row
        print(f"Dairy ID: {dairy_id}")
        print(f"Names in database: {names}")
        
        if names:
            print("\nDatabase normalization:")
            for name in names:
                db_normalized = normalize_dairy_name_database(name)
                print(f"  '{name}' -> '{db_normalized}'")
        
        print("\nWhat I'm trying to match:")
        test_names = [
            "Dickman and Sons Dairy (815)",
            "Dickman (815)"
        ]
        
        for test_name in test_names:
            my_normalized = normalize_dairy_name_my_function(test_name)
            print(f"  '{test_name}' -> '{my_normalized}'")

conn.close() 