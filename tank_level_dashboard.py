import requests
import json
import pandas as pd
from datetime import datetime, timedelta
import time

# API Configuration
SAMSARA_API_TOKEN = "samsara_api_cs6PujA8wahppSXzmUYzAGYmgPqTqE"
VOLUME_FORM_TEMPLATE_ID = "3eb6b1ea-588f-4a46-b405-a3858ae7422e"

headers = {
    "Authorization": f"Bearer {SAMSARA_API_TOKEN}",
    "Accept": "application/json"
}

# Tank capacity and flow rate data (from your actual specifications)
DAIRY_CONFIG = {
    "T&K [Barn 1]": {
        "tanks": {
            "Silo 1": {"capacity": 130000, "flow_rate": 10500},
            "Silo 2": {"capacity": 130000, "flow_rate": 10500},
            "Silo 3": {"capacity": 130000, "flow_rate": 10500}
        }
    },
    "T&K [Barn 2]": {
        "tanks": {
            "Silo 4": {"capacity": 170000, "flow_rate": 10200},
            "Silo 5": {"capacity": 170000, "flow_rate": 10200},
            "Silo 6": {"capacity": 170000, "flow_rate": 10200}
        }
    },
    "T&K [Barn 3]": {
        "tanks": {
            "Silo 7": {"capacity": 170000, "flow_rate": 13400},
            "Silo 8": {"capacity": 170000, "flow_rate": 13400},
            "Silo 9": {"capacity": 170000, "flow_rate": 13400}
        }
    },
    "Milky Way [North Barn]": {
        "tanks": {
            "Tank 1": {"capacity": 110000, "flow_rate": 20000},
            "Tank 2": {"capacity": 110000, "flow_rate": 20000},
            "Tank 3": {"capacity": 110000, "flow_rate": 20000}
        }
    },
    "Milky Way [South Barn]": {
        "tanks": {
            "Tank 4": {"capacity": 110000, "flow_rate": 20000},
            "Tank 5": {"capacity": 110000, "flow_rate": 20000},
            "Tank 6": {"capacity": 110000, "flow_rate": 20000}
        }
    },
    "Triple G [Main Barn]": {
        "tanks": {
            "Silo 1": {"capacity": 120000, "flow_rate": 14500},
            "Silo 2": {"capacity": 120000, "flow_rate": 14500},
            "Silo 3": {"capacity": 120000, "flow_rate": 14500}
        }
    },
    "Legendairy LLC": {
        "tanks": {
            "Tank 1": {"capacity": 60000, "flow_rate": 2500},
            "Tank 2": {"capacity": 60000, "flow_rate": 2500}
        }
    },
    "Piazzo Dairy": {
        "tanks": {
            "Tank 1": {"capacity": 76000, "flow_rate": 11500},
            "Tank 2": {"capacity": 76000, "flow_rate": 11500}
        }
    },
    "Dickman": {
        "tanks": {
            "Tank 1": {"capacity": 78000, "flow_rate": 11500},
            "Tank 2": {"capacity": 78000, "flow_rate": 11500},
            "Tank 3": {"capacity": 78000, "flow_rate": 11500}
        }
    },
    "Belmont": {
        "tanks": {
            "Silo 1": {"capacity": 130000, "flow_rate": 14000},
            "Silo 2": {"capacity": 130000, "flow_rate": 14000}
        }
    },
    "Arizona Dairy": {
        "tanks": {
            "Tank 1": {"capacity": 160000, "flow_rate": 11000},
            "Tank 2": {"capacity": 160000, "flow_rate": 11000}
        }
    },
    "D&I Coolidge (805)": {
        "tanks": {
            "Tank 1": {"capacity": 100000, "flow_rate": 8500},
            "Tank 2": {"capacity": 100000, "flow_rate": 8500}
        }
    },
    "D&I Stanfield (716)": {
        "tanks": {
            "Tank 1": {"capacity": 66000, "flow_rate": 5000},
            "Tank 2": {"capacity": 66000, "flow_rate": 5000}
        }
    }
}

def get_volume_submissions(hours_back=24):
    """Get volume form submissions from the last N hours"""
    url = "https://api.samsara.com/form-submissions/stream"
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours_back)
    
    start_time_str = start_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_time_str = end_time.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    params = {
        'startTime': start_time_str,
        'endTime': end_time_str,
        'formTemplateIds': VOLUME_FORM_TEMPLATE_ID
    }
    
    all_submissions = []
    
    try:
        while True:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code != 200:
                print(f"Error fetching submissions: {response.status_code}")
                break
                
            data = response.json()
            submissions = data.get('data', [])
            all_submissions.extend(submissions)
            
            # Check if there are more pages
            pagination = data.get('pagination', {})
            if not pagination.get('hasNextPage', False):
                break
                
            # Set cursor for next page
            params['after'] = pagination.get('endCursor')
            
        return all_submissions
    except Exception as e:
        print(f"Error: {e}")
        return []

def parse_submission_volumes(submission):
    """Extract volume data from a form submission"""
    volumes = {}
    dairy_name = None
    milking_into = None
    pulled_from = None
    submitted_time = submission.get('submittedAtTime')
    
    fields = submission.get('fields', [])
    
    for field in fields:
        label = field.get('label', '').strip()
        field_type = field.get('type')
        
        # Extract dairy name from checkbox selection - FIXED STRUCTURE
        if 'dairy are you picking up from' in label.lower() and field_type == 'check_boxes':
            if 'checkBoxesValue' in field:
                checkbox_value = field['checkBoxesValue']
                selected_values = checkbox_value.get('value', [])  # Changed from selectedChoices
                if selected_values:
                    dairy_name = selected_values[0]  # Get first selected value
        
        # Extract current milking tank - FIXED: More flexible matching + handle 'miking' typo
        elif ('milking' in label.lower() or 'miking' in label.lower()) and ('into' in label.lower() or 'tank' in label.lower() or 'silo' in label.lower()) and field_type == 'multiple_choice':
            if 'multipleChoiceValue' in field:
                value = field['multipleChoiceValue'].get('value', '')
                if value and value.strip():  # Only use non-empty values
                    milking_into = value
        
        # Extract last pulled tank
        elif 'pull from last' in label.lower() and field_type == 'multiple_choice':
            if 'multipleChoiceValue' in field:
                pulled_from = field['multipleChoiceValue'].get('value', '')
        
        # Extract volume readings
        elif 'volume' in label.lower() and field_type == 'number':
            if 'numberValue' in field:
                volume = field['numberValue'].get('value')
                if volume is not None:
                    # Clean up the label to get tank name
                    tank_name = label.replace('Volume:', '').replace('Volume', '').strip()
                    volumes[tank_name] = volume
    
    return {
        'dairy': dairy_name,
        'volumes': volumes,
        'milking_into': milking_into,
        'pulled_from': pulled_from,
        'timestamp': submitted_time,
        'submission_id': submission.get('id')
    }

def calculate_tank_status(current_data):
    """
    Calculate current tank levels, predicted additions, and other statuses.
    This function processes raw submission data to create a detailed, per-tank status report.
    """
    # Create a dictionary to hold the final status for all dairies and tanks
    tank_statuses = {}

    # Group all submissions by the reported dairy name for efficient processing
    submissions_by_dairy = {}
    for sub in current_data:
        dairy = sub.get('dairy')
        if dairy:
            if dairy not in submissions_by_dairy:
                submissions_by_dairy[dairy] = []
            submissions_by_dairy[dairy].append(sub)

    # Process each dairy defined in the configuration
    for dairy_name, config in DAIRY_CONFIG.items():
        tank_statuses[dairy_name] = {}
        
        # Get all submissions for the current dairy, sorted from most recent to oldest
        dairy_data = sorted(
            [s for s in current_data if s.get('dairy') == dairy_name], 
            key=lambda x: x['timestamp'], 
            reverse=True
        )

        # If there's no data for this dairy in the last 24h, mark all tanks as having no data
        if not dairy_data:
            for tank_name, tank_config in config['tanks'].items():
                tank_statuses[dairy_name][tank_name] = {
                    'current_volume': 0,
                    'base_volume_lbs': 0,
                    'predicted_added_lbs': 0,
                    'last_update': None,
                    'time_to_full_hours': None,
                    'capacity': tank_config.get('capacity'),
                    'is_milking': False,
                    'last_pulled_at': None,
                }
            continue
        
        # The most recent submission for the entire dairy determines what's actively happening
        latest_dairy_submission = dairy_data[0]
        milking_into_tank = latest_dairy_submission.get('milking_into')

        # Process each tank individually
        for tank_name, tank_config in config['tanks'].items():
            # Find the most recent submission that has a volume reading for this specific tank
            latest_tank_submission = None
            matching_volume_key = None
            for s in dairy_data:
                for key in s.get('volumes', {}):
                    # FIXED: Use exact matching or improved matching logic
                    key_clean = key.strip().lower()
                    tank_clean = tank_name.strip().lower()
                    if key_clean == tank_clean or tank_clean in key_clean:
                        latest_tank_submission = s
                        matching_volume_key = key
                        break
                if latest_tank_submission:
                    break
            
            # If there's no reading for this tank, set defaults
            if not latest_tank_submission:
                tank_statuses[dairy_name][tank_name] = {
                    'current_volume': 0,
                    'base_volume_lbs': 0,
                    'predicted_added_lbs': 0,
                    'last_update': None,
                    'time_to_full_hours': None,
                    'capacity': tank_config.get('capacity'),
                    'is_milking': False,
                    'last_pulled_at': None,
                }
                continue
            
            # We have a reading, so let's calculate the status
            base_volume = int(latest_tank_submission['volumes'][matching_volume_key])
            last_update_time = datetime.fromisoformat(latest_tank_submission['timestamp'].replace('Z', '+00:00'))
            
            predicted_added = 0
            time_to_full = None
            is_milking = (tank_name == milking_into_tank)

            # If this tank is the one being milked into, predict how much has been added
            if is_milking:
                time_since_update = (datetime.now(last_update_time.tzinfo) - last_update_time).total_seconds()
                flow_rate_per_hour = tank_config.get('flow_rate', 0) or 0
                
                if flow_rate_per_hour > 0:
                    predicted_added = int((time_since_update / 3600) * flow_rate_per_hour)
                    
                    capacity = tank_config.get('capacity', 0)
                    current_volume = base_volume + predicted_added
                    if current_volume < capacity:
                        remaining_capacity = capacity - current_volume
                        time_to_full = remaining_capacity / flow_rate_per_hour
                else:
                        time_to_full = 0 # It's already full
            
            # Find the last time this specific tank was pulled from
            last_pulled_this_tank_sub = next((s for s in dairy_data if s.get('pulled_from') == tank_name), None)
            last_pulled_at = last_pulled_this_tank_sub['timestamp'] if last_pulled_this_tank_sub else None

            # Determine overall status
            current_total_volume = base_volume + predicted_added
            status = 'Active'
            if current_total_volume >= tank_config.get('capacity', 0) * 0.95:
                status = 'Nearly Full'
            elif current_total_volume >= tank_config.get('capacity', 0):
                status = 'Full'
            elif base_volume == 0:
                status = 'Empty'
            
            # Check if currently being filled
            is_being_filled = (milking_into_tank and tank_name.lower() in str(milking_into_tank).lower())

            # Store all the calculated values - FIXED: Use current_volume instead of current_volume_lbs
            tank_statuses[dairy_name][tank_name] = {
                'current_volume': base_volume + predicted_added,
                'base_volume_lbs': base_volume,
                'predicted_added_lbs': predicted_added,
                'last_update': last_update_time.isoformat(),
                'time_to_full_hours': time_to_full,
                'capacity': tank_config.get('capacity'),
                'is_milking': is_milking,
                'is_being_filled': is_being_filled,
                'status': status,
                'last_pulled_at': last_pulled_at,
            }
    
    return tank_statuses

def format_time_to_full(hours):
    """Convert decimal hours to hours:minutes format"""
    if hours is None or hours <= 0:
        return "N/A"
    
    total_minutes = int(hours * 60)
    if total_minutes < 60:
        return f"{total_minutes}min"
    else:
        hours_part = total_minutes // 60
        minutes_part = total_minutes % 60
        if minutes_part == 0:
            return f"{hours_part}h"
        else:
            return f"{hours_part}h {minutes_part}min"

def format_hours_ago(hours):
    """Convert decimal hours to hours:minutes format for 'ago' display"""
    if hours is None:
        return "Unknown"
    
    total_minutes = int(hours * 60)
    if total_minutes < 60:
        return f"{total_minutes}min ago"
    else:
        hours_part = total_minutes // 60
        minutes_part = total_minutes % 60
        if minutes_part == 0:
            return f"{hours_part}h ago"
        else:
            return f"{hours_part}h {minutes_part}min ago"

def display_dashboard(tank_status):
    """Display the tank level dashboard"""
    print("=" * 80)
    print(f"{'TANK LEVEL STATUS DASHBOARD':^80}")
    print(f"{'Generated at: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'):^80}")
    print("=" * 80)
    
    for dairy_name, tanks in tank_status.items():
        print(f"\n📍 {dairy_name.upper()}")
        print("-" * 70)
        
        for tank_name, data in tanks.items():
            current_vol = data['current_volume']
            predicted_vol = data['predicted_added_lbs']
            capacity = data['capacity']
            time_to_full = data['time_to_full_hours']
            wash_status = data['wash_status']
            status = data['status']
            last_update = data['last_update']
            volume_added = data['predicted_added_lbs']
            
            # Status symbols
            status_symbol = "🟢"
            if status == "Nearly Full":
                status_symbol = "🟡"
            elif status == "Full":
                status_symbol = "🔴"
            elif status == "Empty":
                status_symbol = "⚪"
            elif status == "No Data" or status == "No Reading":
                status_symbol = "❓"
            
            # CORRECTED Wash status color coding
            wash_symbol = "🟢"  # Default green
            if "Wash Time" in wash_status:
                wash_symbol = "🟢"  # Green when ≤5k (wash time)
            elif "CRITICAL" in wash_status:
                wash_symbol = "🔴"  # Red when 48+ hours since ≤5k
            elif "Warning" in wash_status:
                wash_symbol = "🟡"  # Yellow when 24+ hours since ≤5k
            elif "Good" in wash_status:
                wash_symbol = "🟢"  # Green when < 24 hours since ≤5k
            elif "Unknown" in wash_status:
                wash_symbol = "❓"  # Question mark when no data
            
            print(f"  {status_symbol} {tank_name:15} │ ", end="")
            
            if current_vol is not None:
                # Two-color volume display: [current + added]
                print(f"Vol: {current_vol:6,.0f} + {volume_added:4,.0f} = {predicted_vol:6,.0f}/{capacity:6,.0f} lbs │ ", end="")
                
                # Time to full with improved formatting
                time_str = format_time_to_full(time_to_full)
                print(f"Full in: {time_str:>8} │ ", end="")
                
                # Wash status with proper color coding
                print(f"Wash: {wash_symbol} {wash_status:25} │ ", end="")
                
                # Last pulled time - when milk was last taken from this tank
                last_pulled = data.get('last_pulled_at')
                if last_pulled:
                    hours_since_pulled = (datetime.now() - last_pulled.replace(tzinfo=None)).total_seconds() / 3600
                    pulled_ago_str = format_hours_ago(hours_since_pulled)
                    print(f"Last Pulled: {pulled_ago_str}")
                else:
                    print(f"Last Pulled: Never")
            else:
                print(f"{'No data available':>60}")
        
        # Show current milking status
        milking_info = None
        for tank_data in tanks.values():
            if tank_data.get('is_milking'):
                milking_info = tank_data['is_milking']
                break
        
        if milking_info:
            print(f"  🥛 Currently milking into: {milking_info}")

def main():
    print("🚀 Starting Tank Level Dashboard System...")
    print("📡 Fetching volume submissions from Samsara...")
    
    # Get recent form submissions
    submissions = get_volume_submissions(hours_back=72)  # Last 3 days
    print(f"📊 Found {len(submissions)} form submissions")
    
    # Parse submissions to extract volume data
    print("🔍 Parsing volume data...")
    parsed_data = []
    unique_dairies = set()
    
    for submission in submissions:
        parsed = parse_submission_volumes(submission)
        if parsed['dairy']:
            unique_dairies.add(parsed['dairy'])
        if parsed['dairy'] and parsed['volumes']:  # Only include submissions with dairy and volume data
            parsed_data.append(parsed)
    
    print(f"✅ Parsed {len(parsed_data)} submissions with volume data")
    
    # Debug: Show what dairy names we found
    if unique_dairies:
        print(f"🏭 Dairy names found in submissions:")
        for dairy in sorted(unique_dairies):
            print(f"   - '{dairy}'")
    
    # Calculate current tank levels
    print("🧮 Calculating current tank levels...")
    tank_status = calculate_tank_status(parsed_data)
    
    # Display dashboard
    display_dashboard(tank_status)
    
    # Summary statistics
    total_tanks = sum(len(tanks) for tanks in tank_status.values())
    tanks_with_data = sum(1 for tanks in tank_status.values() for tank in tanks.values() if tank['current_volume'] > 0)
    tanks_being_filled = sum(1 for tanks in tank_status.values() for tank in tanks.values() if tank.get('is_milking'))
    tanks_wash_warning = sum(1 for tanks in tank_status.values() for tank in tanks.values() 
                           if 'Warning' in tank['wash_status'] or 'CRITICAL' in tank['wash_status'])
    
    print(f"\n📈 SUMMARY")
    print(f"   Total Dairies: {len(tank_status)}")
    print(f"   Total Tanks: {total_tanks}")
    print(f"   Tanks with Recent Data: {tanks_with_data}")
    print(f"   Data Coverage: {tanks_with_data/total_tanks*100:.1f}%")
    print(f"   Currently Being Filled: {tanks_being_filled}")
    print(f"   Wash Status Warnings: {tanks_wash_warning}")
    
    print(f"\n💡 WASH STATUS LOGIC:")
    print(f"   🟢 Wash Time: Tank currently ≤ 5,000 lbs (ready for wash)")
    print(f"   🟢 Good: < 24hrs since tank was last ≤ 5,000 lbs") 
    print(f"   🟡 Warning: 24-48hrs since tank was last ≤ 5,000 lbs")
    print(f"   🔴 CRITICAL: 48+ hrs since tank was last ≤ 5,000 lbs (milk waste risk!)")
    print(f"   ❓ Unknown: No recent ≤5k reading found")
    
    print(f"\n⚠️  CRITICAL tanks need immediate attention to prevent milk waste!")
    print(f"   Schedule pickup to pump tank back down to ≤5k and reset wash timer.")

if __name__ == "__main__":
    main() 