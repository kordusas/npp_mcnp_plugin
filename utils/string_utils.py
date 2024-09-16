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