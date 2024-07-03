
from Npp import console

# Add the format_notifier_message function
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
    
def log_debug(debug, message):
    """
    Log a debug message to the console.

    Args:
        message (str): The message to log.
    """
    if debug:
        console.write(message)

        