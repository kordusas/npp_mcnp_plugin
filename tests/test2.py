import json
import os

def find_macrobody_by_surface_type(surface_type, json_data):
    """
    This function searches for a macrobody in the JSON data by surface type.

    Args:
        surface_type (str): The surface type to search for.
        json_data (dict): The JSON data to search in.

    Returns:
        dict: The macrobody information if found, otherwise None.
    """
    for key, value in json_data.items():
        if "macrobody" in key and value["prefix"][0].lower() == surface_type.lower():
            return value["body"]
    return None

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Define the path to the JSON file
json_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'mcnp.tmSnippets.json'))

# Read the JSON data
physics_and_macrobodies_info = read_json_file(json_file_path)

# Define the surface type to search for
surface = "WED"

# Call the function and print the result
result = find_macrobody_by_surface_type(surface, physics_and_macrobodies_info)
print(result)
print(type(result))