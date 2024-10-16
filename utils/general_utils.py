from Npp import console
import logging
import os, json
# Add the format_notifier_message function
def initialise_json_data( filename):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, '..', 'data', filename)
        with open(file_path, 'r') as json_file:
            surface_info = json.load(json_file)
        return surface_info

def validate_return_id_as_int(id):
    # Step 1: Validate and Convert material_id
    if isinstance(id, str):
        try:
            id = int(id)
        except ValueError:
            # Handle the case where conversion is not possible
            id = None
            # print error message using logging
            logging.error("Invalid id '{}' provided. Expected an integer.".format(id))
    return id

def format_notifier_message(items_to_show):
    """
    Formats message for the notifier into a string.
    Args:
        items_to_show (str | list | object): The items to format into a message string.
    Returns:
        str: The formatted message.
    """
    if items_to_show is None:
        return None
    elif isinstance(items_to_show, str):
        return items_to_show
    elif isinstance(items_to_show, list):
        return '\n'.join([str(item) for item in items_to_show])
    else:  # Assuming it's an object instance
        return str(items_to_show)

def configure_logging(enable_logging=True):
    logging_level = logging.DEBUG if enable_logging else logging.CRITICAL
    logging.basicConfig(level=logging_level)
def get_char_from_args(args):
    try:
        return chr(args['ch'])
    except Exception as e:
        console.write("Error in on_character_added: {}".format(str(e)))
        return None
    


def find_by_key_and_prefix(search_prefix, json_data, search_key_string=None):
    """
    This function searches through JSON data to find entries with a matching prefix in the value
    and an optional search string in the key.

    Args:
        search_prefix (str): The prefix to match within the value's prefix field.
        json_data (dict): The JSON data to search in.
        search_key_string (str, optional): The string to search for in the keys. Defaults to None.

    Returns:
        dict: The information associated with the matching entry if found, otherwise None.
    """
    for key, value in json_data.items():
        if search_key_string is not None and search_key_string not in key.lower():
            continue
        if value["prefix"][0].lower() == search_prefix:
            return value.get("body")
    return None   