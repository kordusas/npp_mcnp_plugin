from Npp import editor, console
from mcnp_utils import Surface, Tally, Transformation, Material
from general_utils import log_debug
import re

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
 
class ViewOfLine(object):
    """
    This class is used to interact with the current line of the text editor. creates model representation of the line.
    """
    def __init__(self, debug=True):
        self.selected_text = editor.getSelText().lower()
        self.debug = debug
        self._initialize_view_properties()
        
    def _initialize_view_properties(self):
        self.selected_text = editor.getSelText().lower()
        self.selection_start = editor.getSelectionStart()
        self.selection_end = editor.getSelectionEnd()
        self.cursor_column = editor.getColumn(editor.getCurrentPos())
        self.current_line_no = editor.lineFromPosition(editor.getCurrentPos())
        self.current_line = self._get_line_without_comment(self.current_line_no)

    def is_selection_after_pattern(self, pattern):
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
    def is_continuation_line(self):
        return self.current_line.startswith('    ')
    @property
    def is_empty_line(self):
        return self.current_line.strip() == ""  
    @property
    def selection_is_empty(self):
        return self.selected_text.strip() == ""
    @property
    def is_comment_line(self):
        return self.current_line.lstrip().startswith('c') 
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
    
    def _get_line_without_comment(self, current_line_no):
        """
        Returns the current line without the comment part.
        """
        current_line = editor.getLine(current_line_no).lower()
        if "$" in current_line:
            current_line = current_line.split("$", 1)[0]
        return current_line

    def get_full_mcnp_input_line(self):
        if not self.is_continuation_line:
            return self.selected_text
        return self._merge_continuation_lines()

    def _merge_continuation_lines(self):
        full_line_parts = [self.selected_text]
        line_offset = 1
        while True:
            try:
                previous_line = self._get_previous_line(line_offset)
            except IndexError:
                break

            if not self._is_continuation(previous_line):
                break

            full_line_parts.insert(0, previous_line.rstrip())
            line_offset += 1

        return ''.join(full_line_parts)

    def _get_previous_line(self, line_offset):
        return self._get_line_without_comment(self.current_line_no - line_offset)

    def _is_continuation(self, line):
        return line.startswith('    ')
    


class FileParser(object):
    def __init__(self,filename, debug=True):
        self.filename = filename
        self.lines = None
        self.message_block = None
        self.cells_block = None
        self.surfaces_block = None
        self.physics_block = None
        self.has_header = False
        self.block_locations = {}
        self.title  = ""
        self.debug = debug
         
    def set_header_flag(self):
        # Determine if we have a header block
        self.has_header = self.lines[0].startswith("message")

    def set_block_locations(self):
        """
        Finds and returns the different blocks of data in the file.

        Returns:
            block_locations (dict): The start and end lines of each block.
        """
        log_debug(True, "Finding blocks...\n")

        block_start_indices = []
        
        for i, line in enumerate(self.lines):
            if line.strip() == "":
                block_start_indices.append(i)
        
        if self.has_header:
            self.parse_header(block_start_indices[0])
            block_start_indices[0] += 1 # adding 1 as this is empty line
        else:
            block_start_indices.insert(0, 0)
        
        # +2 because first line is always a title
        self.block_locations['cells'] = {'start': block_start_indices[0]+1, 'end': block_start_indices[1]}
        self.block_locations['surfaces'] = {'start': block_start_indices[1], 'end': block_start_indices[2]}
        self.block_locations['physics'] = {'start': block_start_indices[2], 'end': len(self.lines)}
                
        return 0
    def parse_header(self, line_no):
        self.message_block = self.lines[:line_no]

    def parse_title(self):
        self.title = self.lines[self.block_locations['cells']['start']-1]
    def parse_blocks(self):
        self.cells_block = self.format_blocks(self.lines[self.block_locations['cells']['start']:self.block_locations['cells']['end']])
        self.surfaces_block = self.format_blocks(self.lines[self.block_locations['surfaces']['start'] + 1:self.block_locations['surfaces']['end']])
        self.physics_block = self.format_blocks(self.lines[self.block_locations['physics']['start'] + 1:])

    def parse(self):
        """
        Parses the different blocks of data in the file.
        I merge the continuation lines for better interpretation of the data.

        """
        self.parse_blocks()
        self.parse_title()

        console.write("Cells block: {}\nSurfaces block: {}\nPhysics block: {}\n".format(
            len(self.cells_block), len(self.surfaces_block), len(self.physics_block)
        ))
    def get_cells(self):
        pass
    def get_materials(self):
        pass
    def get_tallies(self):
        pass
    def get_physics(self):
        pass
    def get_surfaces(self):
        """
        returns the parsed surface dictionary
        parsed surfaces indexed by their ID.

        Returns:
            parsed_surfaces (dict): A dictionary of `Surface` objects representing the parsed surfaces,
                                    indexed by their surface ID.
        """
        parsed_surfaces = {}
        comment = ""
        for line in self.surfaces_block:
            if line.startswith("c"):
                comment += line
                continue
            surface = self.parse_surface(line, comment)
            parsed_surfaces[int(surface.surface_id)] = surface
            comment = ""
        return parsed_surfaces
    
    def parse_surface(self, line, comment=""):
        """
        Parses a single surface line and returns a `Surface` object.

        Args:
            line (str): The line to parse.
            comment (str): The comment associated with the surface.

        Returns:
            surface (Surface): The parsed `Surface` object.
        """
        surface_data = line.split("$")
        if len(surface_data) >= 2:
            comment = surface_data[1].strip()
        
        surface_data = surface_data[0].split()
        if len(surface_data) >= 3:
            surface_id = surface_data[0]
            if surface_data[1].isdigit():
                surface_transform = surface_data[1]
                surface_type = surface_data[2]
                surface_params = ' '.join(surface_data[3:])
            else:
                surface_transform = None
                surface_type = surface_data[1]
                surface_params = ' '.join(surface_data[2:])
            surface = Surface(surface_id, surface_type, surface_params, comment, surface_transform)
            console.write("Surface parsed: {}\n".format(surface_id))
        else:
            console.write("Error parsing surface: {}\n".format(line))
            surface = None
        return surface
       
    def analyse_file(self):
        self.set_header_flag()
        self.set_block_locations()
        self.parse()

    def read_new_file(self, file_path):
        self.filename = file_path
        self.read_file()
        self.analyse_file()

    def read_file(self):
        """
        Determines if the specified line is in the surfaces block.

        Args:
            line (str): The line to check.

        Returns:
            bool: True if the line is in the surfaces block, False otherwise.
        """
        if self.block_locations['surfaces']['start'] <= line_number <= self.block_locations['surfaces']['end']:
            is_in_surface_block = True
        else:
            is_in_surface_block = False
        return is_in_surface_block
    
    def is_in_physics_block(self, line_number):
        """
        Determines if the specified line is in the physics block.

        Args:
            line (str): The line to check.

        Returns:
            bool: True if the line is in the physics block, False otherwise.
        """
        if self.block_locations['physics']['start'] <= line_number <=  self.block_locations['physics']['end'] :
            is_in_physics_block = True
        else:
            is_in_physics_block = False
        return is_in_physics_block
    
    def analyse_file(self):
        self.find_blocks()
        self.parse_blocks()
        
    @classmethod
    def from_file(cls, file_path, debug=True):
        """
        Class method to create an instance of FileParser from a file path.
        """
        instance = cls(file_path)

        instance.debug = debug
        instance.read_file()
        instance.analyse_file()
        
        log_debug(True,"Parsed {} lines from file: {}\n".format(len(instance.lines), file_path) )  
        
        return instance
 
        

