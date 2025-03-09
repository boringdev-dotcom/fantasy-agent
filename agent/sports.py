import os
import json
import requests

def load_sports_data():
    """Load sports data from API instead of JSON file"""
    try:
        # Call the API to get sports data
        api_url = "http://localhost:8000/api/sports"
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Parse the JSON response
        sports_data = response.json()
        print(f"Successfully loaded {len(sports_data)} sports from API")
        return sports_data
    except Exception as e:
        print(f"Error loading sports data from API: {e}")
        print("Falling back to local sports.json file...")
        
        # Fallback to local JSON file if API call fails
        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sports_file_path = os.path.join(script_dir, 'sports.json')
            
            with open(sports_file_path, 'r') as f:
                sports_data = json.load(f)
            print(f"Successfully loaded {len(sports_data)} sports from local file")
            return sports_data
        except Exception as e2:
            print(f"Error loading sports data from file: {e2}")
            return []

# Load sports data
# sports_data = load_sports_data()
# currently using only 3 sports for testing
# load_sports_data
sports_data = []

# Create a mapping of sport_id to sport_name for easy reference
sport_id_to_name = {sport['id']: sport['name'] for sport in sports_data}

# Create a formatted string of all supported sports
def format_sports_for_prompt():
    if not sports_data:
        return "7 for NBA, 2 for NFL, 82 for Soccer"
    
    sports_list = [f"{sport['id']} for {sport['name']}" for sport in sports_data]
    return ", ".join(sports_list)

# Create a more detailed mapping for the prompt
def create_sports_mapping_text():
    if not sports_data:
        return "NBA = 7, NFL = 2, Soccer = 82"
    
    mappings = [f"{sport['name']} = {sport['id']}" for sport in sports_data]
    return ", ".join(mappings)