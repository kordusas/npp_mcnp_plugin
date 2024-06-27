from Npp import editor
import re
class ViewOfLine():
    """
    This class is used to interact with the current line of the text editor. creates model representation of the line.
    """
    def __init__(self, debug=True):
        self.text = editor.getSelText().lower()
        self.selection_start = editor.getSelectionStart()
        self.selection_end = editor.getSelectionEnd()
        self.cursor_column = editor.getColumn(editor.getCurrentPos())
        self.current_line_no = editor.lineFromPosition(editor.getCurrentPos())
        self.current_line = editor.getLine(self.current_line_no).lower()
        self.debug = debug
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
        return self.text.split()
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
    def is_continuation_line(self):
        return self.current_line.startswith('    ')
    @property
    def is_empty_line(self):
        return self.current_line.strip() == ""  
    @property
    def selection_is_empty(self):
        return self.text.strip() == ""
    @property
    def is_comment_line(self):
        return self.current_line.strip().startswith('c') 
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
        log_debug(self.debug, "Called method is_lattice_line\n")
        full_line = self.get_full_mcnp_input_line()
        if "fill" in self.current_line:
            fill_index = self.current_line.find("fill")
            if self.cursor_column > fill_index:
                return True
        if "fill" in full_line:
                return True

        return False
    
    def get_full_mcnp_input_line(self):
        """
        Prepend the full MCNP input line if the current line is a continuation line.
        """
        if not self.is_continuation_line:
            return self.text

        full_line_parts = [self.text]
        line_offset = 1
        while True:
            try:
                previous_line = editor.getLine(self.current_line_no - line_offset).rstrip()
            except IndexError:  # Reached the beginning of the document
                break

            if not previous_line.startswith('    '):
                break

            full_line_parts.insert(0, previous_line)
            line_offset += 1

        return ''.join(full_line_parts)
    


class FileParser():
    """
    This class parses the file and creates mcnp_input object.
    """
    def __init__(self):
            pass
    
    def get_surfaces(self):
        """
        This function returns the surfaces from the parsed file.
        """
        pass
    def get_cells(self):
        """
        This function returns the cells from the parsed file.
        """
        pass    
    def get_materials(self):
        """
        This function returns the materials from the parsed file.
        """
        pass
    def get_tallies(self):
        """
        This function returns the tallies from the parsed file.
        """
        pass
    def get_physics(self):
        """
        This function returns the physics from the parsed file.
        """
        pass
    def parse_file(self):
        """ 
        This function parses the file.
        """