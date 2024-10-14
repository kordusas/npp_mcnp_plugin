import sys
import os

# Add the parent directory to the sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Try to import the necessary modules and handle import errors
try:
    from presenters.presenter_utils import find_macrobody_by_surface_type
    from utils.general_utils import initialise_json_data
except ImportError as e:
    print("ImportError: {}".format(e))
    find_macrobody_by_surface_type = None
    initialise_json_data = None

if initialise_json_data and find_macrobody_by_surface_type:
    # Initialize the JSON data
    physics_and_macrobodies_info = initialise_json_data("mcnp.tmSnippets.json")

    # Define the surface type to search for
    surface = "WED"

    # Call the function and print the result
    result = find_macrobody_by_surface_type(surface, physics_and_macrobodies_info)
    print(result)
else:
    print("Required functions are not available due to import errors.")