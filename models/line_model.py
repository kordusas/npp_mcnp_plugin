
from Npp import editor
import logging, re
from npp_mcnp_plugin.utils.string_utils import is_comment_line

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

    @property
    def current_line(self):
        """
        Returns the current line of the text editor.
        """
        return self._get_line_without_comment(self.current_line_no).lstrip()
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
    

    # Helper method for regular expressions (example)
    def _find_last_number_in_string(self, string):
        try:
            return re.findall(r'\d+', string)[-1]
        except IndexError:
            return None

    @property
    def last_number_in_line(self):
        return self._find_last_number_in_string(self.current_line)
    @property
    def last_number_before_cursor(self):
        return self._find_last_number_in_string(self.text_till_cursor)
    
    @property
    def last_entry_before_cursor(self):
        try:
            last_entry = self.text_till_cursor.split()[-1]
            return last_entry
        except IndexError:
            return None  # Or any default value or action       
        
    @property
    def is_lattice_line(self):
        """ This method checks if the current line is a lattice line.
            There are two possible options to check if the current line is a lattice line:
            1. If the keyword 'fill' is present in the current line and the selection start position is after the 'fill' keyword, the line is considered a lattice line.
            2. If the current line is a continuation line (starts with four spaces)  the text from the previous line(s) is prepended to the current line until a non-continuation line is encountered. If the resulting text contains the keyword 'fill', the line is considered a lattice line.
        """
        self.logger.debug("Called method is_lattice_line")
        
        if "fill" in self.current_line:
            fill_index = self.current_line.find("fill")
            if self.cursor_column > fill_index:
                return True
        # checking if there is keyword fill earlier
        if "fill" in self.full_mcnp_input_line:
                return True

        return False
    
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
    def full_mcnp_input_line(self):
        if not self.is_continuation_line:
            return self.current_line
        return self._merge_continuation_lines()

    def _merge_continuation_lines(self):
        """
        Merges continuation lines into a single line by iterating through
        previous lines that are marked as continuation lines.

        This function collects parts of the current and previous lines that
        are considered continuation lines, strips leading spaces, and combines
        them into a single string.

        Returns:
            str: A single string representing the merged continuation lines,
            with leading spaces removed and the continuation character '&'
            stripped from the end.
        """
        full_line_parts = []
        line_number = self.current_line_no

        # Start with the current line, cleaned of comments and leading spaces
        previous_line = self._get_line_without_comment(line_number).lstrip()

        # Continue processing as long as the line is a continuation line or a comment line
        while self.is_continuation_line(line_number) or is_comment_line(previous_line):
            # Add the previous line if it's not a comment
            if not is_comment_line(previous_line):
                full_line_parts.append(previous_line)

            # Move to the previous line
            try:
                line_number -= 1
                previous_line = self._get_line_without_comment(line_number).lstrip()
            except IndexError:
                break

        # Join all parts and strip any '&' at the end
        return ' '.join(reversed(full_line_parts)).strip("&")




    def find_space_separated_token_end_positions(self, token_index, pattern=r'\S+'):
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