from Npp import console
import logging
import re
# Add the format_notifier_message function

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
    if isinstance(items_to_show, str):
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


def is_match_at_start(line, regex_pattern):
    """
    checks if line starts with a specific regex pattern
    """
    return bool(re.match(regex_pattern, line))