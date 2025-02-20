import re
import logging


from npp_mcnp_plugin.models.mcnp_input_cards import Surface, Tally, Transformation, Material
from npp_mcnp_plugin.models.mcnp_cell_factory import CellFactory
from npp_mcnp_plugin.models.error import  ErrorModel
from npp_mcnp_plugin.utils.string_utils import is_comment_line, is_match_at_start

_REPEAT_RE = re.compile(r'(\d+)\s+(\d+)[rR]')
class FileParser(object):
    def __init__(self, filename, error_collection):
        self.filename = filename

        self.error_collection = error_collection
        self.content = None
        self.lines = None
        self.block = {}
        self.block_locations = {}
        self.title  = ""
        self.logger = logging.getLogger(self.__class__.__name__)
    def _parse_block(self, block, regex_pattern, create_instance_func):
        """
        Generic method to parse a block of lines based on a regex pattern and create instances using a provided function.
        Captures instance errors and passes them to the error collector.

        Args:
            regex_pattern (str): The regex pattern to match lines.
            create_instance_func (function): The function to create an instance from a match object and comment.

        Returns:
            dict: A dictionary of parsed instances indexed by their ID.
        """
        parsed_items = {}
        comment = ""
        pattern = re.compile(regex_pattern)
        try:
            for line in block:
                match = pattern.match(line)
                if match:
                    instance = create_instance_func(match, comment)
                    if instance:
                        self.logger.debug("Created instance: %s", instance)
                        parsed_items[instance.id] = instance
                    comment = ""
                elif is_comment_line(line):
                    comment += " " + re.sub(' +', ' ', line.lstrip("c"))
                else:
                    comment = ""
        except Exception as e:
            error_message = "Error while processing line '{}': {}".format(line, e)
            self.logger.error(error_message)
            self.error_collection.add_error(
                ErrorModel(line, e, "INVALID_DATA")
            )
        return parsed_items

    def get_transformations(self):
        self.logger.debug("Parsing transformations")
        return self._parse_block(self.block["physics"],
            regex_pattern=r"\*?tr\d",
            create_instance_func=Transformation.create_from_match
        )

    def get_materials(self):
        self.logger.debug("Parsing materials")
        return self._parse_block(self.block["physics"],
            regex_pattern=r'm(\d+)(.*)',
            create_instance_func=Material.create_from_match,
        )

    def get_tallies(self):
        self.logger.debug("Parsing tallies")
        return self._parse_block(self.block["physics"],
            regex_pattern=r'^(\+?f)(\d+)\:?(\S+)?(.*)',
            create_instance_func=Tally.create_from_match,
        )
    def get_surfaces(self):
        self.logger.debug("Parsing surfaces")
        return self._parse_block(self.block["surfaces"],
            regex_pattern=r'^\d+(.*)',
            create_instance_func=Surface.create_from_match,
        )
    def get_cells(self):
        self.logger.debug("Parsing cells")
        return self._parse_block(self.block["cells"],
            regex_pattern=r'(\d+)\s+(\d+)\s+(.*)',
            create_instance_func=CellFactory.create_from_match,
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

    def analyse_file(self):
        self.format_sanitize_content()
        self.split_blocks()
        self.format_sanitize_blocks()


    @staticmethod
    def count_block_start_locations( sections):
        block_start_indices = []
        line_number = 0  # Initialize line_number
        for section in sections:
        # Count newlines up to this section
            line_number += section.count('\n')
            line_number += 2
            block_start_indices.append((line_number, section.strip()))
            
        return block_start_indices
    
    def split_blocks(self):

        sections = re.split(r'\n[ \t]*\n', self.content)
        block_start_indices = self.count_block_start_locations(sections)
        # count number of new lines in each block and append to block_start_indices list 
        if sections[0].startswith("\s+message"):
            self.block["message"] = sections[0]
            sections = sections[1:]
            block_start_indices = block_start_indices[1:]
        else:
            block_start_indices.insert(0, (0, ''))
            
        self.block["cells"] = sections[0]   
        self.block["surfaces"] = sections[1]
        self.block["physics"] = sections[2]

        self.block_locations['cells'] = {'start': block_start_indices[0][0] , 'end': block_start_indices[1][0] }
        self.block_locations['surfaces'] = {'start': block_start_indices[1][0] , 'end': block_start_indices[2][0] }
        self.block_locations['physics'] = {'start': block_start_indices[2][0] , 'end': block_start_indices[3][0] if len(block_start_indices) > 3 else len(self.content.splitlines())}
        # clearing memory
        self.content = []
        
                
    def format_sanitize_blocks(self):
        for key in self.block.keys():
            # Turn continuation lines into single line
            self.block[key] = re.sub(' &.*\n', ' ', self.block[key])
            self.block[key] = re.sub('\n {5}', ' ', self.block[key])

            
            # Remove all leading spaces after newlines
            self.block[key] = re.sub(r'\n +', '\n', self.block[key])         

            # Expand repeated numbers
            m = _REPEAT_RE.search(self.block[key])
            while m is not None:
                self.block[key] = _REPEAT_RE.sub(' '.join((int(m.group(2)) + 1)*[m.group(1)]),
                                        self.block[key], 1)
                m = _REPEAT_RE.search(self.block[key])    
                
            # Split into lines and merge comments/continuations
            
            self.logger.debug("sanitized %s block content: %s", key, self.block[key])
            self.block[key] = self.block[key].splitlines()

    def format_sanitize_content(self):
        self.content = self.content.lower() # make everything lowercase
        self.content = re.sub(r'\(', ' (', self.content) # adding space before the ( (handling some edge case like this cell: 1 10 -2.0(3 4 5) 6 7 8 9)

        # removing comments which are in the middle of the cards
        self.content = re.sub('^[ \t]*?[cC].*?$\n {5}?', '', self.content, flags=re.MULTILINE)

        self.content = re.sub(r'\$.*$', '', self.content, flags=re.MULTILINE) # remove inline comments   
        

    def read_new_file(self, file_path):
        self.filename = file_path
        self.read_file()
        self.analyse_file()

    def read_file(self):
        """
        Reads the file.
        """
        try:
            with open(self.filename, 'r') as file:
                self.content = file.read()  # Assign the content to self.content
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



