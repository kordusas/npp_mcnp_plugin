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
        self.debug = debug
        self._initialize_view_properties()
        
    def _initialize_view_properties(self):
        self.selected_text = self.selected_text = editor.getSelText().lower().split("imp")[0].strip()
        self.selection_start = editor.getColumn(editor.getSelectionStart())
        self.selection_end = editor.getColumn(editor.getSelectionEnd())
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

            if not self.is_continuation_line(self.current_line_no-line_offset):
                break

            full_line_parts.insert(0, previous_line.rstrip())
            line_offset += 1

        return ''.join(full_line_parts).strip("&")

    def _get_previous_line(self, line_offset):
        return self._get_line_without_comment(self.current_line_no - line_offset)
        
    def find_space_separated_token_end_positions(self, token_index):
        """
        Finds the position immediately after the first character of a specified space-separated token in a string.

        This method identifies positions in the string where a space separates two alphanumeric or special character tokens
        (e.g., '+', '-', '*', '/', '(', ')'). It returns the position immediately after the first character of the specified
        space-separated token, based on a 0-indexed token_index.

        Parameters:
        - token_index (int): The index of the token for which to find the end position, where indexing starts at 0.

        Returns:
        - int: The position immediately after the first character of the specified space-separated token.
        """
        pattern = r'([a-zA-Z0-9+\-*/()])(\s+)([a-zA-Z0-9+\-*/()])'
        matches = re.finditer(pattern, self.current_line)
        # As this returns the end o
        end_positions = [match.start()+1 for match in matches]
        return end_positions[token_index] if token_index < len(end_positions) else None

    


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

    def format_blocks(self, block):
        """
        removes leading spaces if less than 4 spaces 

        Merges continuation lines in the file.
        If the line starts with 4 spaces, it is a continuation line.
        If the line has a comment after a '$', it is appended to comment_line
        the comment_line is then appended to the previous line.

        If accidenally the line is empty we skip it.
        """
        merged_block = []
        comment = ""
        for  line in block:
            # strip the continuation sign which may be present in some cases but not all
            line = line.rstrip('\n')

            # formatting the line and comment
            line, comment = self.split_comment_from_line(line, comment)

            # remove continue line character at the end of line
            line = line.rstrip('&')
            
            if line.strip() == "":
                continue
            # if lines starts with less than 4 spaces then remove them
            elif len(line) - len(line.lstrip(' ')) < 4:
                line = line.lstrip(' ')


            # merging the continuation lines
            if line.startswith("    "):
                merged_block[-1] += line
            else:
                merged_block.append(line) # Add the current line to merged_block
                if comment:
                    # insert this comment as one before the last element
                    merged_block.insert(-2, "c " + comment.strip() + "\n")
                    comment = ""  # Reset comment after inserting

        return merged_block
    
    def _parse_cell(self):
        pass

    def get_cells(self):
        pass

    def get_transformations(self):
        transformations = {}
        comment = ""
        for line in self.physics_block:
            # match one optional "*" which is followed by tr and then at least one digit
            if is_match_at_start(line, regex_pattern="^(?:\*?tr\d)"):
                transformation_instance = Transformation.create_from_input_line(line, comment)
                transformations[transformation_instance.id] = transformation_instance
                comment = ""
            elif line.startswith("c"):
                comment += line
            else:
                comment = ""

        return transformations       

    def get_materials(self):
        materials = {}
        comment = ""
        for line in self.physics_block:
            if  is_match_at_start(line, regex_pattern= 'm(\d+)(.*)'):
                log_debug(self.debug, "Material text: {}\n Material comment: {}\n".format(line, comment))
                material_instance = Material.create_from_input_line(line,  comment)
                log_debug(self.debug, "Material instance: {}\n".format(material_instance))
                materials[material_instance.id] = material_instance
                comment = ""
            elif line.startswith("c"):
                comment += line
            else:
                comment = ""

        return materials

    def get_tallies(self):
        tallies = {}
        comment = ""
        for line in self.physics_block:
            if  is_match_at_start(line, regex_pattern= '^f\d+:'):
                tally_instance = Tally.create_from_input_line(line,  comment)
                tallies[tally_instance.id] = tally_instance
                comment = ""
            elif line.startswith("c"):
                comment += line
            else:
                comment = ""

        return tallies

    def get_physics(self):
        information_dict = {}
        for line in self.physics_block:
            if line.startswith("kcode"):
                # parse source object
                information_dict['kcode'] = line
            elif line.startswith("mode"):
                # parse mode
                # drop mode and split line according to spaces and commas into a list
                mode_particle_list = re.sub(r"[,mode]", " ", line)
                    
                information_dict['mode'] = mode_particle_list

            elif line.startswith("nps"):
                # parse nps
                information_dict['nps'] = int(float(line.split()[1]))
        return information_dict

    def split_comment_from_line(self, line, comment=""):
        """
        Splits the comment from the line and returns the line and comment separately.
        if comment doesnt exist does nothing
        Args:
            line (str): The line to split.

        Returns:
            line (str): The line without the comment.
            comment (str): The comment.
        """
        comment_new = ""        
        if "$" in line:
            line, comment_new = line.split("$", 1)

        # stripping the line  from right side to remove any trailing spaces
        return line.rstrip(" "), comment + comment_new
               


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
            parsed_surfaces[surface.id] = surface
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
        comment = ""
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
            surface = Surface(int(surface_id), surface_type, surface_params, comment, surface_transform)
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
        Reads the file and stores the lines in the `lines` attribute in lower case.
        """
        try:
            with open(self.filename, 'r') as file:
                self.lines = [line.lower() for line in file.readlines()]
        except Exception as e:
            log_debug(True, "Error reading file: {}\n".format(str(e))) 
        
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
 
        

