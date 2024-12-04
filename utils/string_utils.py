import re
import logging
def get_block_type_from_line(model_of_line):
    """
    Determine the block type of the given line based on regex patterns.

    Args:
        model_of_line: An object with the attribute 'full_mcnp_input_line' containing the line to classify.

    Returns:
        str: The block type, one of ['surfaces', 'cells', 'physics'].
    """
    # Fetch the full line for evaluation
    full_mcnp_input_line = model_of_line.full_mcnp_input_line.strip()
    logging.debug("full line: %s", full_mcnp_input_line)
    # Define regex patterns for each block type
    patterns = {
        'surfaces': [
            r'^\d+\s+\d+\s+[a-zA-Z]+\s+\d+',  # First 'surfaces' pattern
            r'^\d+\s+(?!like\b)[a-zA-Z]+\s+\d+',         # Second 'surfaces' pattern
        ],
        'cells': [
            r'^\d+\s+\d+\s+\S+\s+.*',           # 'cells' pattern
            r'^\d+\s+like\s+\d+but\s+.*',
        ]
    }
    
    # Check the line against each pattern in order
    for block_type, regex_list in patterns.items():
        for pattern in regex_list:
            if re.match(pattern, full_mcnp_input_line):
                return block_type
    
    # If no patterns match, default to 'physics'
    return 'physics'

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

def extract_keyword_value(line, keyword):
        """
        Extracts the value associated with a keyword in a string.

        Args:
            line: The input string.
            keyword: The keyword to search for.

        Returns:
            The value associated with the keyword, or None if the keyword is not found.
        """
        match = re.search(r'{}\s*=\s*(\S+)'.format(keyword), line)
        return match.group(1) if match else None