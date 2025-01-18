import json
import datetime

def load_api_key(api_key_name):
    credentials_path = '/app/credentials.json'
    if not credentials_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable is not set.")
    
    # Load the JSON credentials file
    with open(credentials_path, 'r') as file:
        credentials = json.load(file)
    
    return credentials.get(api_key_name)

def format_datetime(input_datetime_str: str, input_format: str = '%Y-%m-%dT%H:%M:%SZ', output_format: str = '%Y-%m-%d %H:%M:%S') -> str:
    """Convert a datetime string from one format to another."""
    if input_datetime_str:
        try:
            # Parse the input datetime string
            parsed_datetime = datetime.datetime.strptime(input_datetime_str, input_format)
            # Return the formatted datetime string
            return parsed_datetime.strftime(output_format)
        except ValueError as e:
            # Handle parsing errors
            return None  # Return None if the input string is not valid
    return None  # Return None if the input string is empty
