
from Npp import console


def log_debug(debug, message):
    """
    Log a debug message to the console.

    Args:
        message (str): The message to log.
    """
    if debug:
        console.write(message)

        