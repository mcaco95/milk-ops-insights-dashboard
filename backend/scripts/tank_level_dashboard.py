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
    "D & I Holsteins": {
        "tanks": {
            "Tank 1": {"capacity": 100000, "flow_rate": 8500},
            "Tank 2": {"capacity": 100000, "flow_rate": 8500}
        }
    },
    "AZ Dairy": {
        "tanks": {
            "Tank 1": {"capacity": 160000, "flow_rate": 11000},
            "Tank 2": {"capacity": 160000, "flow_rate": 11000}
        }
    },
    "D&I Dairy": {
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
        
        # Extract current milking tank
        elif 'milking into' in label.lower() and field_type == 'multiple_choice':
            if 'multipleChoiceValue' in field:
                milking_into = field['multipleChoiceValue'].get('value', '')
        
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
    """Calculate current tank levels with time to full and wash status"""
    predictions = {}
    
    # Updated dairy mapping to match actual form choices
    dairy_mapping = {
        "T&K [Barn 1]": "T&K [Barn 1]",
        "T&K [Barn 2]": "T&K [Barn 2]", 
        "T&K [Barn 3]": "T&K [Barn 3]",
        "Milky Way [North Barn]": "Milky Way [North Barn]",
        "Milky Way [South Barn]": "Milky Way [South Barn]",
        "Triple G [Main Barn]": "Triple G [Main Barn]",
        "Legendairy LLC": "Legendairy LLC",
        "Piazzo Dairy": "Piazzo Dairy",
        "Dickman": "Dickman",
        "Belmont": "Belmont",
        "D & I Holsteins": "D & I Holsteins",
        "AZ Dairy": "AZ Dairy",
        "D&I Dairy": "D&I Dairy"
    }
    
    for dairy_name, config in DAIRY_CONFIG.items():
        predictions[dairy_name] = {}
        
        # Find the most recent data for this dairy using mapping
        dairy_data = []
        for d in current_data:
            if d['dairy']:
                mapped_dairy = dairy_mapping.get(d['dairy'], d['dairy'])
                if dairy_name.lower() in mapped_dairy.lower():
                    dairy_data.append(d)
        
        if not dairy_data:
            # No recent data, show all tanks as unknown
            for tank_name, tank_config in config['tanks'].items():
                predictions[dairy_name][tank_name] = {
                    'current_volume': None,
                    'predicted_volume': None,
                    'last_update': None,
                    'volume_added_since': 0,
                    'time_to_full_hours': None,
                    'wash_status': 'Unknown',
                    'status': 'No Data',
                    'capacity': tank_config['capacity'],
                    'milking_into': None,
                    'pulled_from': None,
                    'last_pulled_time': None
                }
            continue
        
        # Get the most recent submission for this dairy
        latest_submission = max(dairy_data, key=lambda x: x['timestamp'])
        last_update = datetime.fromisoformat(latest_submission['timestamp'].replace('Z', '+00:00'))
        
        for tank_name, tank_config in config['tanks'].items():
            capacity = tank_config['capacity']
            flow_rate = tank_config['flow_rate']  # lbs per hour
            
            # Find volume reading for this tank
            current_volume = None
            for volume_field, volume_value in latest_submission['volumes'].items():
                # More flexible matching for tank names
                tank_clean = tank_name.lower().replace(' ', '')
                field_clean = volume_field.lower().replace(' ', '')
                if tank_clean in field_clean or field_clean in tank_clean:
                    current_volume = volume_value
                    break
            
            if current_volume is None:
                predictions[dairy_name][tank_name] = {
                    'current_volume': None,
                    'predicted_volume': None,
                    'last_update': last_update,
                    'volume_added_since': 0,
                    'time_to_full_hours': None,
                    'wash_status': 'Unknown',
                    'status': 'No Reading',
                    'capacity': capacity,
                    'milking_into': latest_submission.get('milking_into'),
                    'pulled_from': latest_submission.get('pulled_from'),
                    'last_pulled_time': None
                }
                continue
            
            # Calculate time since last reading
            hours_since_reading = (datetime.now() - last_update.replace(tzinfo=None)).total_seconds() / 3600
            
            # Only add volume if currently milking into this tank
            volume_added = 0
            if (latest_submission.get('milking_into') and 
                tank_name.lower() in latest_submission['milking_into'].lower()):
                volume_added = hours_since_reading * flow_rate
            
            current_predicted_volume = current_volume + volume_added
            
            # Calculate time to full (only if currently milking into this tank)
            time_to_full_hours = None
            if volume_added > 0:  # Only if currently being filled
                remaining_capacity = capacity - current_predicted_volume
                if remaining_capacity > 0 and flow_rate > 0:
                    time_to_full_hours = remaining_capacity / flow_rate
            
            # CORRECTED WASH STATUS LOGIC
            # Find when this tank was last at ≤5k lbs to start wash timer
            wash_status = 'Good'
            last_wash_time = None
            
            # Look through historical data to find when tank was last ≤5k
            for data_point in sorted(dairy_data, key=lambda x: x['timestamp'], reverse=True):
                for vol_field, vol_value in data_point['volumes'].items():
                    tank_clean = tank_name.lower().replace(' ', '')
                    field_clean = vol_field.lower().replace(' ', '')
                    if tank_clean in field_clean or field_clean in tank_clean:
                        if vol_value <= 5000:  # Found when tank was last at wash level
                            wash_time = datetime.fromisoformat(data_point['timestamp'].replace('Z', '+00:00'))
                            last_wash_time = wash_time
                            break
                if last_wash_time:
                    break
            
            # Calculate wash status based on time since last ≤5k reading
            if current_volume <= 5000:
                wash_status = 'Wash Time (≤5k)'
            elif last_wash_time:
                hours_since_wash = (datetime.now() - last_wash_time.replace(tzinfo=None)).total_seconds() / 3600
                if hours_since_wash >= 48:
                    wash_status = f'CRITICAL ({hours_since_wash:.0f}h since ≤5k)'
                elif hours_since_wash >= 24:
                    wash_status = f'Warning ({hours_since_wash:.0f}h since ≤5k)'
                else:
                    wash_status = f'Good ({hours_since_wash:.0f}h since ≤5k)'
            else:
                wash_status = 'Unknown (no ≤5k reading found)'
            
            # Find when milk was last PULLED FROM this specific tank
            last_pulled_time = None
            for data_point in sorted(dairy_data, key=lambda x: x['timestamp'], reverse=True):
                pulled_from = data_point.get('pulled_from', '')
                if pulled_from and tank_name.lower() in pulled_from.lower():
                    last_pulled_time = datetime.fromisoformat(data_point['timestamp'].replace('Z', '+00:00'))
                    break
            
            # Determine overall status
            status = 'Active'
            if current_predicted_volume >= capacity * 0.95:
                status = 'Nearly Full'
            elif current_predicted_volume >= capacity:
                status = 'Full'
            elif current_volume == 0:
                status = 'Empty'
            
            # Check if currently being filled
            is_being_filled = (latest_submission.get('milking_into') and 
                             tank_name.lower() in latest_submission['milking_into'].lower())
            
            predictions[dairy_name][tank_name] = {
                'current_volume': current_volume,
                'predicted_volume': min(current_predicted_volume, capacity),
                'last_update': last_update,
                'volume_added_since': volume_added,
                'time_to_full_hours': time_to_full_hours,
                'wash_status': wash_status,
                'status': status,
                'capacity': capacity,
                'milking_into': latest_submission.get('milking_into'),
                'pulled_from': latest_submission.get('pulled_from'),
                'is_being_filled': is_being_filled,
                'last_wash_time': last_wash_time,
                'last_pulled_time': last_pulled_time
            }
    
    return predictions

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
            predicted_vol = data['predicted_volume']
            capacity = data['capacity']
            time_to_full = data['time_to_full_hours']
            wash_status = data['wash_status']
            status = data['status']
            last_update = data['last_update']
            volume_added = data['volume_added_since']
            
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
                last_pulled = data.get('last_pulled_time')
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
            if tank_data.get('milking_into'):
                milking_info = tank_data['milking_into']
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
    tanks_with_data = sum(1 for tanks in tank_status.values() for tank in tanks.values() if tank['current_volume'] is not None)
    tanks_being_filled = sum(1 for tanks in tank_status.values() for tank in tanks.values() if tank.get('is_being_filled'))
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