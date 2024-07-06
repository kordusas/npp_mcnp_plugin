from Npp import editor, console
from mcnp_utils import Surface
from general_utils import log_debug
import re

def get_char_from_args(args):
    try:
        return chr(args['ch'])
    except Exception as e:
        console.write("Error in on_character_added: {}".format(str(e)))
        return None
    
class ViewOfLine(object):
    """
    This class is used to interact with the current line of the text editor. creates model representation of the line.
    """
    def __init__(self, debug=True):
        self.selected_text = editor.getSelText().lower()
        self.selection_start = editor.getSelectionStart()
        self.selection_end = editor.getSelectionEnd()
        self.cursor_column = editor.getColumn(editor.getCurrentPos())
        self.current_line_no = editor.lineFromPosition(editor.getCurrentPos())
        self.current_line = editor.getLine(self.current_line_no).lower()
        self.debug = debug
    
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
            return self.selected_text

        full_line_parts = [self.selected_text]
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
    


class FileParser(object):
    def __init__(self):
        self.filename = []
        self.lines = []
        self.message_block = []
        self.cells_block = []
        self.surfaces_block = []
        self.physics_block = []
        self.has_header = False
        self.block_locations = {}
        self.title  = ""

    def find_blocks(self):
        """
        Finds and returns the different blocks of data in the file.

        Returns:
            block_locations (dict): The start and end lines of each block.
        """
        console.write("Finding blocks...\n")

        block_start_indices = []
        # Determine if we have a header block
        self.has_header = self.lines[0].startswith("message")

        block_start_indices = []
        for i, line in enumerate(self.lines):
            if line.strip() == "":
                block_start_indices.append(i)
        
        if self.has_header:
            self.message_block = self.lines[:block_start_indices[0]]
            block_start_indices[0] += 1 # adding 1 as this is empty line
        else:
            block_start_indices.insert(0, 0)
        
        # +2 because first line is always a title
        self.block_locations['cells'] = {'start': block_start_indices[0]+1, 'end': block_start_indices[1]}
        self.block_locations['surfaces'] = {'start': block_start_indices[1], 'end': block_start_indices[2]}
        self.block_locations['physics'] = {'start': block_start_indices[2], 'end': len(self.lines)}
                
        return 0

    def parse_blocks(self):
        """
        Parses the different blocks of data in the file.

        """
        self.title = self.lines[self.block_locations['cells']['start']-1]
        self.cells_block = self.lines[self.block_locations['cells']['start']:self.block_locations['cells']['end']]
        self.surfaces_block = self.lines[self.block_locations['surfaces']['start'] + 1:self.block_locations['surfaces']['end']]
        self.physics_block = self.lines[self.block_locations['physics']['start'] + 1:]

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
    
    def is_in_cell_block(self, line_number):
        """
        Determines if the specified line is in the cells block.

        Args:
            line (str): The line to check.

        Returns:
            bool: True if the line is in the cells block, False otherwise.
        """
        if  self.block_locations['cells']['start'] <= line_number <= self.block_locations['cells']['end']:
            is_in_cell_block = True
        else:
            is_in_cell_block = False
        return is_in_cell_block
    
    def is_in_surface_block(self, line_number):
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
    def from_file(cls, file_path):
        """
        Class method to create an instance of FileParser from a file path.
        """
        instance = cls()

        instance.filename = file_path
        instance.lines = []
        try:
            with open(file_path, 'r') as file:
                for i, line in enumerate(file, 1):
                    instance.lines.append(line.lower())
        except Exception as e:
           log_debug(True,"Error reading file: {}\n".format(str(e)) )  
        
        log_debug(True,"Parsed {} lines from file: {}\n".format(len(instance.lines), file_path) )  
        instance.analyse_file()
        return instance
 
        


