#!/usr/bin/env python3
"""
Fetch Samsara addresses and generate SQL for database initialization
Run this locally to generate SQL statements that can be added to init_db.sql
"""

import requests
import json

# Samsara API configuration
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"

def get_auth_headers():
    """Returns the authorization headers for Samsara API."""
    return {"Authorization": f"Bearer {SAMSARA_API_TOKEN}", "Accept": "application/json"}

def fetch_samsara_addresses():
    """Fetch all addresses from Samsara API."""
    print("Fetching addresses from Samsara API...")
    url = "https://api.samsara.com/addresses"
    
    try:
        response = requests.get(url, headers=get_auth_headers())
        response.raise_for_status()
        
        addresses = response.json().get('data', [])
        print(f"Successfully fetched {len(addresses)} addresses from Samsara")
        return addresses
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching addresses from Samsara: {e}")
        return []

def generate_sql_statements(addresses):
    """Generate SQL statements for database initialization."""
    if not addresses:
        print("No addresses to generate SQL for")
        return
    
    print("\n" + "="*80)
    print("SQL STATEMENTS FOR init_db.sql")
    print("="*80)
    
    # Table creation
    print("""
-- Create Samsara addresses table
CREATE TABLE IF NOT EXISTS samsara_addresses (
    id SERIAL PRIMARY KEY,
    samsara_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address_line_1 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_samsara_addresses_name ON samsara_addresses(name);
CREATE INDEX IF NOT EXISTS idx_samsara_addresses_location ON samsara_addresses(latitude, longitude);
""")
    
    print("-- Insert Samsara addresses")
    print("INSERT INTO samsara_addresses (samsara_id, name, latitude, longitude, address_line_1, city, state, zip_code) VALUES")
    
    values = []
    for addr in addresses:
        # Extract address components
        samsara_id = addr.get('id', '').replace("'", "''")  # Escape quotes
        name = addr.get('name', 'Unknown').replace("'", "''")
        latitude = addr.get('latitude')
        longitude = addr.get('longitude')
        
        # Parse formatted address
        formatted_address = addr.get('formattedAddress', '')
        address_line_1 = ''
        city = ''
        state = ''
        zip_code = ''
        
        if formatted_address:
            parts = formatted_address.split(',')
            if len(parts) >= 1:
                address_line_1 = parts[0].strip().replace("'", "''")
            if len(parts) >= 2:
                city = parts[1].strip().replace("'", "''")
            if len(parts) >= 3:
                state_zip = parts[2].strip()
                state_zip_parts = state_zip.split()
                if len(state_zip_parts) >= 2:
                    state = state_zip_parts[0].replace("'", "''")
                    zip_code = state_zip_parts[1].replace("'", "''")
        
        # Format SQL value
        lat_str = str(latitude) if latitude is not None else 'NULL'
        lng_str = str(longitude) if longitude is not None else 'NULL'
        
        value = f"('{samsara_id}', '{name}', {lat_str}, {lng_str}, '{address_line_1}', '{city}', '{state}', '{zip_code}')"
        values.append(value)
    
    # Print values in chunks to avoid too long lines
    for i, value in enumerate(values):
        if i == len(values) - 1:  # Last item
            print(f"  {value};")
        else:
            print(f"  {value},")
    
    print("\n-- Query to verify addresses were loaded")
    print("SELECT COUNT(*) as address_count FROM samsara_addresses;")
    print("SELECT name, latitude, longitude FROM samsara_addresses WHERE latitude IS NOT NULL LIMIT 10;")

def print_json_backup(addresses):
    """Print addresses as JSON backup."""
    print("\n" + "="*80)
    print("JSON BACKUP (for reference)")
    print("="*80)
    print(json.dumps(addresses, indent=2))

def main():
    """Main function to fetch and print Samsara addresses."""
    print("=== SAMSARA ADDRESSES FETCHER ===")
    
    # Fetch addresses from Samsara
    addresses = fetch_samsara_addresses()
    if not addresses:
        print("No addresses fetched, exiting")
        return
    
    # Generate SQL statements
    generate_sql_statements(addresses)
    
    # Print summary
    print(f"\n✅ Generated SQL for {len(addresses)} Samsara addresses!")
    print("Copy the SQL statements above and add them to your init_db.sql file")
    
    # Optionally save to file
    save_to_file = input("\nSave SQL to file? (y/n): ").lower().strip()
    if save_to_file == 'y':
        with open('samsara_addresses.sql', 'w') as f:
            f.write("-- Samsara Addresses for Database Initialization\n")
            f.write("-- Generated automatically from Samsara API\n\n")
            
            # Write table creation
            f.write("""CREATE TABLE IF NOT EXISTS samsara_addresses (
    id SERIAL PRIMARY KEY,
    samsara_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    address_line_1 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_samsara_addresses_name ON samsara_addresses(name);
CREATE INDEX IF NOT EXISTS idx_samsara_addresses_location ON samsara_addresses(latitude, longitude);

""")
            
            # Write insert statements
            f.write("INSERT INTO samsara_addresses (samsara_id, name, latitude, longitude, address_line_1, city, state, zip_code) VALUES\n")
            for i, addr in enumerate(addresses):
                samsara_id = addr.get('id', '').replace("'", "''")
                name = addr.get('name', 'Unknown').replace("'", "''")
                latitude = addr.get('latitude')
                longitude = addr.get('longitude')
                
                formatted_address = addr.get('formattedAddress', '')
                address_line_1 = ''
                city = ''
                state = ''
                zip_code = ''
                
                if formatted_address:
                    parts = formatted_address.split(',')
                    if len(parts) >= 1:
                        address_line_1 = parts[0].strip().replace("'", "''")
                    if len(parts) >= 2:
                        city = parts[1].strip().replace("'", "''")
                    if len(parts) >= 3:
                        state_zip = parts[2].strip()
                        state_zip_parts = state_zip.split()
                        if len(state_zip_parts) >= 2:
                            state = state_zip_parts[0].replace("'", "''")
                            zip_code = state_zip_parts[1].replace("'", "''")
                
                lat_str = str(latitude) if latitude is not None else 'NULL'
                lng_str = str(longitude) if longitude is not None else 'NULL'
                
                terminator = ';' if i == len(addresses) - 1 else ','
                f.write(f"  ('{samsara_id}', '{name}', {lat_str}, {lng_str}, '{address_line_1}', '{city}', '{state}', '{zip_code}'){terminator}\n")
        
        print("✅ SQL saved to samsara_addresses.sql")

if __name__ == "__main__":
    main() 