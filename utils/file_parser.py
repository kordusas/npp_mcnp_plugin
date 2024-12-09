from npp_mcnp_plugin.models.mcnp_input_cards import Surface, Tally, Transformation, Material, CellFactory
from npp_mcnp_plugin.models.error import  ErrorModel
from npp_mcnp_plugin.utils.string_utils import is_comment_line, is_match_at_start

import re
import logging

class FileParser(object):
    def __init__(self, filename, error_collection):
        self.filename = filename

        self.error_collection = error_collection
        self.lines = None
        self.message_block = None
        self.has_header = False
        self.block = {}
        self.block_locations = {}
        self.title  = ""
        self.logger = logging.getLogger(self.__class__.__name__)
         
    def set_header_flag(self):
        # Determine if we have a header block
        self.has_header = self.lines[0].startswith("message")

    def set_block_locations(self):
        """
        Finds and sets the start and end lines of each block of data in the file.

        This method identifies the indices of empty lines in the file, which are used to determine the boundaries of different blocks of data (cells, surfaces, and physics). It then sets the start and end lines for each block in the `block_locations` attribute. If a header is present, it adjusts the indices accordingly.

        Returns:
            None
        """
        self.logger.info("Called method set_block_locations...\n")

        block_start_indices = []
        offset = 1  # Offset to account for the title line and empty lines

        for i, line in enumerate(self.lines):
            if line.strip() == "":
                block_start_indices.append(i)

        if self.has_header:
            self.parse_header(block_start_indices[0])
            block_start_indices[0] += offset  # adding offset as this is an empty line
        else:
            block_start_indices.insert(0, 0)

        self.block_locations['cells'] = {'start': block_start_indices[0] + offset, 'end': block_start_indices[1]}
        self.block_locations['surfaces'] = {'start': block_start_indices[1] + offset, 'end': block_start_indices[2]}
        self.block_locations['physics'] = {'start': block_start_indices[2] + offset, 'end': block_start_indices[3] + offset if len(block_start_indices) > 3 else len(self.lines)}
                
        return 
    def parse_header(self, line_no):
        self.message_block = self.lines[:line_no]

    def parse_title(self):
        self.title = self.lines[self.block_locations['cells']['start']-1]
    def parse_blocks(self):
        for key in ['cells','surfaces', 'physics']:
            self.block[key] =self.format_blocks(self.lines[self.block_locations[key]['start']:self.block_locations[key]['end']])
  

    def parse(self):
        """
        Parses the different blocks of data in the file.
        I merge the continuation lines for better interpretation of the data.

        """
        self.parse_blocks()
        self.parse_title()

        self.logger.info("Cells block: %d\nSurfaces block: %d\nPhysics block: %d\n",
            len(self.block["cells"]), len(self.block["surfaces"]), len(self.block["physics"])
        )

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
            
            line = line.rstrip('\n')
            if line.strip() == "":
                continue
            # formatting the line and comment
            line, comment = self.split_comment_from_line(line, comment)
           
            
            # if lines starts with less than 4 spaces then remove them
            line = self._remove_leading_spaces(line)

            # merging the continuation lines
            if not merged_block:
                self._add_new_line(merged_block, line, comment)
                comment = ""
            elif line.startswith("    ") or merged_block[-1].endswith('&'):
                merged_block[-1] = merged_block[-1].rstrip('&') + line
            elif line.startswith("c"):
                comment += " " + line[1:]
            else:
                self._add_new_line(merged_block, line, comment)
                comment = ""

        return merged_block
    
    def _remove_leading_spaces(self, line):
        """
        Removes leading spaces from a line if there are fewer than 4 spaces.

        This method is used to handle indentation in MCNP input files. Lines with
        fewer than 4 leading spaces are treated as new entries, while lines with
        4 or more spaces are considered continuation lines.

        Args:
            line (str): The input line to process.

        Returns:
            str: The line with leading spaces removed if there were fewer than 4,
                 otherwise the original line.
        """
        if len(line) - len(line.lstrip(' ')) < 4:
            return line.lstrip(' ')
        return line
    def _add_new_line(self, merged_block, line, comment):
        merged_block.append(line)
        if comment:
            merged_block.insert(-2, "c " + comment.replace("--", "").replace("==", "").replace("||", "").strip())    

    def _parse_block(self, block, regex_pattern, create_instance_func):
        """
        Generic method to parse a block of lines based on a regex pattern and create instances using a provided function.
        Captures instance errors and passes them to the error collector

        Args:
            regex_pattern (str): The regex pattern to match lines.
            create_instance_func (function): The function to create an instance from a line and comment.

        Returns:
            dict: A dictionary of parsed instances indexed by their ID.
        """
        parsed_items = {}
        comment = ""
        try:
            for line in block:
                if is_match_at_start(line, regex_pattern=regex_pattern):

                    # returns instance and error message if any during the instance creation
                    instance = create_instance_func(line, comment)
                    
                    if instance:
                        self.logger.debug("Created instance: %s", instance)
                        parsed_items[instance.id] = instance
                    comment = ""

                elif is_comment_line(line):
                    comment += " " + re.sub(' +', ' ', line.lstrip("c"))
                else:
                    comment = ""
                    
        except Exception as e:
                # Catch any exception, log it, and add it to the error collection
                error_message = "Error while processing line '{}': {}".format(line, e)
                self.logger.error(error_message)
                self.error_collection.add_error(
                    ErrorModel(line, e, "INVALID_DATA")
                )
        return parsed_items

    def get_transformations(self):
        self.logger.debug("Parsing transformations")
        return self._parse_block(self.block["physics"],
            regex_pattern="\*?tr\d",
            create_instance_func=Transformation.create_from_input_line
        )

    def get_materials(self):
        self.logger.debug("Parsing materials")
        return self._parse_block(self.block["physics"],
            regex_pattern='m(\d+)(.*)',
            create_instance_func=Material.create_from_input_line,
        )

    def get_tallies(self):
        self.logger.debug("Parsing tallies")
        return self._parse_block(self.block["physics"],
            regex_pattern='^(\+?f)(\d+)\:?',
            create_instance_func=Tally.create_from_input_line,
        )
    def get_surfaces(self):
        self.logger.debug("Parsing surfaces")
        return self._parse_block(self.block["surfaces"],
            regex_pattern='^\d+',
            create_instance_func=Surface.create_from_input_line,
        )
    def get_cells(self):
        self.logger.debug("Parsing cells")
        return self._parse_block(self.block["cells"],
            regex_pattern='(\d+)\s+(\d+)\s+(\S+)\s+(.*)',
            create_instance_func=CellFactory.create_from_input_line,
        )    
    def get_physics(self):
        information_dict = {}
        for line in self.block["physics"]:
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
            self.logger.exception("Error reading file: {}\n".format(str(e))) 
        
    @classmethod
    def from_file(cls, file_path, error_collection):
        """
        Class method to create an instance of FileParser from a file path.
        """
        instance = cls(file_path, error_collection)

        
        instance.read_file()
        instance.analyse_file()
        instance.logger.info("FileParser created from file: %s", file_path)  

        return instance
 
        

