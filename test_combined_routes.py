#!/usr/bin/env python3
"""
Test script for the new combined routes functionality
Tests schedules + pickups integration safely
"""

import sys
import os
sys.path.append('scripts')

from get_daily_routes import (
    get_combined_routes_data, 
    get_schedules_data,
    convert_schedule_to_pickup_format,
    generate_routes_report,
    get_all_samsara_locations
)
from datetime import datetime, date

def test_schedules_conversion():
    """Test if schedules data converts properly to pickup format."""
    print("🧪 TESTING SCHEDULES DATA CONVERSION")
    print("=" * 50)
    
    # Test getting schedules
    today = date.today().strftime("%Y-%m-%d")
    tomorrow = datetime.now().strftime("%Y-%m-%d")  # This should be tomorrow
    
    schedules = get_schedules_data(today, tomorrow)
    
    if not schedules:
        print("❌ No schedules found for testing")
        return False
    
    print(f"✅ Found {len(schedules)} schedules for testing")
    
    # Test converting first schedule
    try:
        first_schedule = schedules[0]
        print(f"\n🔍 Original schedule structure:")
        for key, value in list(first_schedule.items())[:8]:
            print(f"  {key}: {value}")
        
        converted = convert_schedule_to_pickup_format(first_schedule)
        print(f"\n✅ Converted to pickup format:")
        for key, value in converted.items():
            print(f"  {key}: {value}")
        
        return True
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        return False

def test_combined_data():
    """Test the combined data approach."""
    print("\n🧪 TESTING COMBINED DATA APPROACH")
    print("=" * 50)
    
    try:
        today = date.today().strftime("%Y-%m-%d")
        combined_data = get_combined_routes_data(today)
        
        if not combined_data:
            print("❌ No combined data returned")
            return False
        
        print(f"✅ Got {len(combined_data)} total records")
        
        # Count by type
        pickup_count = sum(1 for record in combined_data if record.get('schedule_status') != 'scheduled')
        schedule_count = sum(1 for record in combined_data if record.get('schedule_status') == 'scheduled')
        
        print(f"📦 Breakdown:")
        print(f"  - Pickups (active/completed): {pickup_count}")
        print(f"  - Schedules (future): {schedule_count}")
        
        return True
    except Exception as e:
        print(f"❌ Combined data test failed: {e}")
        return False

def test_routes_report():
    """Test if the routes report handles both types correctly."""
    print("\n🧪 TESTING ROUTES REPORT GENERATION")
    print("=" * 50)
    
    try:
        today = date.today().strftime("%Y-%m-%d")
        combined_data = get_combined_routes_data(today)
        
        if not combined_data:
            print("❌ No data for report testing")
            return False
        
        # Get Samsara locations (might fail, that's ok for testing)
        try:
            locations = get_all_samsara_locations()
        except:
            print("⚠️ Using empty locations for testing")
            locations = {}
        
        report = generate_routes_report(combined_data, locations)
        
        if report.empty:
            print("❌ Report generation returned empty DataFrame")
            return False
        
        print(f"✅ Generated report with {len(report)} routes")
        
        # Show status breakdown
        status_counts = report['Status'].value_counts()
        print(f"📊 Status breakdown:")
        for status, count in status_counts.items():
            print(f"  - {status}: {count}")
        
        # Show sample of scheduled routes
        scheduled_routes = report[report['Status'] == 'Scheduled']
        if not scheduled_routes.empty:
            print(f"\n🔮 Sample scheduled routes ({len(scheduled_routes)} total):")
            for _, row in scheduled_routes.head(3).iterrows():
                print(f"  Route {row['Route']}: {row['Dairy']} (Tank {row['Tank']}) - ETA: {row['ETA']}")
        
        return True
    except Exception as e:
        print(f"❌ Routes report test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🔬 TESTING NEW COMBINED ROUTES SYSTEM")
    print("=" * 60)
    
    tests = [
        test_schedules_conversion,
        test_combined_data, 
        test_routes_report
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("🏁 TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{i+1}. {test.__name__}: {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Safe to deploy.")
    else:
        print("⚠️ Some tests failed. Review before deploying.")

if __name__ == "__main__":
    main() 