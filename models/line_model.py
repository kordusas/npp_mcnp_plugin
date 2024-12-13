
from Npp import editor
import logging, re
from npp_mcnp_plugin.utils.string_utils import is_comment_line, remove_comments, return_last_number_in_string

class ModelOfLine(object):
    """
    This class is used to interact with the current line of the text editor. creates model representation of the line.
    """
    def __init__(self, selected_text=None, cursor_column=None, current_line_no=None, selection_start=None, selection_end=None):
        
        self.selected_text = selected_text
        self.cursor_column = cursor_column
        self.current_line_no = current_line_no

        self.selection_start = selection_start
        self.selection_end = selection_end
        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def from_notepad(cls):
        selected_text = editor.getSelText().lower().split("imp")[0].strip()
        selection_start = editor.getColumn(editor.getSelectionStart())
        selection_end = editor.getColumn(editor.getSelectionEnd())
        cursor_column = editor.getColumn(editor.getCurrentPos())
        current_line_no = editor.lineFromPosition(editor.getCurrentPos())
        instance = cls( selected_text, cursor_column, current_line_no,selection_start,selection_end)

        return instance

    def get_line(self, line_no):
        """
        Fetches a specific line from the editor by line number.

        If an exception occurs, logs the error, continues execution, 
        and returns a line containing "0".
        """
        try:
            current_line = editor.getLine(line_no).lower()
        except Exception as e:
            self.logger.exception(
                "Error fetching line {}: {}. Returning default line '0'.".format(line_no, str(e))
            )
            return "0"
        
        line, comment = remove_comments(current_line)
        return line
    
    @property
    def current_line(self):
        """
        Returns the current line from the editor.
        """
        line, comment = remove_comments(self.get_line(self.current_line_no))
        return line
    
    def is_pattern_before_cursor(self, pattern):
        return pattern in self.text_till_cursor
        
    @property
    def first_entry_in_line(self):
        try:
            return self.current_line_list[0]
        except IndexError:
            return None  # Or any default value or action
    @property
    def first_entry_in_selection(self):
        try:
            return self.selected_text_list[0]
        except IndexError:
            return None  # Or any default value or action
    @property
    def selected_text_list(self):
        return self.selected_text.split()
    @property
    def current_line_list(self):
        return self.current_line.split()
    @property
    def text_till_cursor(self):
        return self.current_line[:self.cursor_column]
    @property
    def text_till_cursor_list(self):
        return self.current_line[:self.cursor_column].split()
    
    @property
    def has_non_digit_chars_before_cursor(self):
        """
        Checks if there are non-digit characters before the cursor in the current line.
        """
        return any(char.isalpha() for char in self.text_till_cursor)

    @property
    def last_number_in_line(self):
        return return_last_number_in_string(self.current_line)
    @property
    def last_number_before_cursor(self):
        return return_last_number_in_string(self.text_till_cursor)
    
    @property
    def last_entry_before_cursor(self):
        try:
            last_entry = self.text_till_cursor.split()[-1]
            return last_entry
        except IndexError:
            return None  # Or any default value or action       
   
    def find_space_separated_token_end_position(self, token_index, pattern=r'\S+'):
        """
        Finds the position immediately after the first character of a specified space-separated token in a string.

        This method identifies positions in the string where a space separates characters based on the provided pattern.

        Parameters:
        - token_index (int): The index of the token for which to find the end position, where indexing starts at 0.
        - pattern (str): The regular expression pattern to identify tokens. Default is r'\S+'. we locate space separated tokens and find where it ends in the line

        Returns:
        - int: The position immediately after the first character of the specified space-separated token.
        """
        matches = list(re.finditer(pattern, self.current_line))
        if token_index < len(matches):
            match = matches[token_index]
            return match.end()
        return None

class BaseLineHelper(object):
    """
    Abstract base class for line helpers in Python 2.7.
    Provides common methods for analyzing lines and handling continuation logic.
    """
    __metaclass__ = ABCMeta

    def __init__(self, model_of_line):
        """
        Initializes the helper with a ModelOfLine instance.

        :param model_of_line: An instance of ModelOfLine representing the current line.
        """
        self.model_of_line = model_of_line

    def is_continuation_line(self, line_no):
        """
        Determines if a specific line is a continuation line.

        :param line_no: The line number to check.
        :return: True if the line is a continuation line, False otherwise.
        """
        current_line, _ = remove_comments(self.model_of_line.get_line(line_no))
        if current_line and current_line.startswith("    "):
            return True

        previous_line = remove_comments(self.model_of_line.get_line(line_no - 1))
        return bool(previous_line and previous_line.endswith("&"))

    def is_current_line_continuation_line(self):
        """
        Determines if the current line is a continuation line.

        :return: True if the current line is a continuation line, False otherwise.
        """
        return self.is_continuation_line(self.model_of_line.current_line_no)
    @property
    def is_cursor_at_material(self):
        """
        Determine if the cursor is at a material definition 
        only usable within a cell block.

        Returns:
            bool: True if the cursor is at a material definition, False otherwise.
        """
        # strip line into list, if there is only two elements in the list then it is likely we are adding a material
        return len(self.text_till_cursor_list) == 2 

    @property
    def is_current_line_continuation_line(self):
        return self.is_continuation_line(self.current_line_no)
    
    def is_continuation_line(self, line_number=0):
        """
        answers if current line is a continuation line or not
        takes argument the line number of the line to check

        two cases when it is a continuation line:
        - line starts with at least 4 spaces
        - previous line ends with & character
        """
        line = self._get_line_without_comment(line_number)
        if line.startswith('    '):
            return True
       
        previous_line = self._get_line_without_comment(line_number - 1)
        return previous_line.endswith('&')
    def _get_line_without_comment(self, current_line_no):
        """
        Returns the current line without the comment part.
        - stripped right side for empty spaces
        - cant strip left side for leading spaces as this may mark a continuation line.
        """
        current_line = editor.getLine(current_line_no).lower()
        if "$" in current_line:
            current_line = current_line.split("$", 1)[0]
        return current_line.rstrip()
    @property
    def full_entry(self):
        # if current line or next line is continuation line then return full line
        if  self.is_current_line_continuation_line or self.is_continuation_line(self.current_line_no+1):
            return self._merge_continuation_lines()
        return self.current_line 

    def _merge_continuation_lines(self):
        """
        Merges continuation lines into a single complete input card by finding the 
        start of the card and collecting all continuation lines up to the current line.

        Collects parts of the lines, strips leading spaces, and removes the 
        continuation character '&' from the end.

        Returns:
            str: The merged full input card as a single string.
        """
        full_line_parts = []
        current_line_no = self.current_line_no
        is_new_card_start = lambda line_no, content: (
        not self.is_continuation_line(line_no) and not is_comment_line(content)
    )
        
        # Move backwards to find the start of the card (non-continuation and non-comment line)
        while current_line_no >= 0:
            current_line = self._get_line_without_comment(current_line_no).lstrip()

            # If it's not a continuation or a comment, we've found the start of the card
            if is_new_card_start(current_line_no, current_line):
                self.logger.debug("Card start found, line no %s", current_line_no)
                break
            # Move to the previous line
            current_line_no -= 1

        # Continue processing as long as the next line is a continuation line or a comment line
        while True:

            if not is_comment_line(current_line):
                full_line_parts.append(current_line)

            # Move to the previous line
            
            current_line_no += 1
            # Start with the current line, cleaned of comments and leading spaces
            try:
                current_line = self._get_line_without_comment(current_line_no).lstrip()
            except IndexError:
                self.logger.warning("Couldn't find end of mcnp input card")
                break

            if is_new_card_start(current_line_no, current_line):
                break
        # Join all parts and strip any '&' at the end
        return ' '.join(full_line_parts).strip("&")