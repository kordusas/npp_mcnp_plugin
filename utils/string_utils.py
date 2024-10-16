import re

def is_comment_line(line):
    """
    Checks if a line starts with a comment.

    Args:
        line (str): The line to check.

    Returns:
        bool: True if the line starts with a comment, False otherwise.
    """
    return line.lstrip().startswith('c')

def is_string_empty(line):
        return line.strip() == ""

def is_match_at_start(line, regex_pattern):
    """
    checks if line starts with a specific regex pattern
    """
    return bool(re.match(regex_pattern, line))

def return_list_entries_starting_with_string(my_list, string):
    """
    Returns a list of entries from the input list that start with the specified string.

    Args:
        my_list (list): The list of entries to search through.
        string (str): The string to match at the start of each entry.

    Returns:
        list: A list of entries that start with the specified string.
    """
    return [str(key) for key in my_list if str(key).startswith(string)]