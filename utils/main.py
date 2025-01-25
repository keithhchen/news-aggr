import json
import os
import datetime

def load_api_key(api_key_name):
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key_name = api_key_name.upper()
    env_value = os.environ.get(api_key_name)
    if not env_value:
        raise ValueError(f"Environment variable {api_key_name} not found")    
    return env_value

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
