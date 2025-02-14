import logging
import re
try: 
    from npp_mcnp_plugin.utils.general_utils import validate_return_id_as_int
    from mcnp_input_cards import  Cell
except ImportError:
    from utils.general_utils import validate_return_id_as_int
    from models.mcnp_input_cards import  Cell

class CellFactory:
    """
    Factory for creating and parsing Cell instances.
    """
    logger = logging.getLogger(__name__)
    cell_keywords = [
            r'\*?trcl', r'\*?fill', 'tmp', 'u', 'lat',
            'imp:.', 'vol', 'pwt', 'ext:.', 'fcl', 'wwn', 'dxc', 'nonu', 'pd',
            'elpt', 'cosy', 'bflcl', 'unc', 
        ]
    any_keyword = '|'.join(['(?:{})'.format(k) for k in cell_keywords])
    
    
    @staticmethod
    def create_from_input_line(line, comment=None):
        """
        Parses an input line and creates a Cell instance.
        """
        pattern = re.compile(r'(\d+)\s+(\d+)\s+(\S+.*)?')
        match = pattern.search(line)
        if not match:
            CellFactory.logger.error("Input line format is invalid: %s", line)
            raise ValueError("Input line format is invalid")
        return CellFactory.create_from_match(match, comment)

    @staticmethod
    def create_from_match(match, comment=None):
        """
        Creates a Cell instance from a regex match object.

        Args:
            match (re.Match): The regex match object containing cell information.
            comment (str, optional): An optional comment associated with the cell.

        Returns:
            Cell: A Cell instance created from the parsed information.
        """
        cell_id = validate_return_id_as_int(match.group(1))
        material_id = validate_return_id_as_int(match.group(2))
        cell_definition, keyword_dict = CellFactory.extract_keywords(match.group(3))

        if "like" in cell_definition and "but" in cell_definition:
            return Cell(cell_id, 0)
        
        trimmed_line, density = CellFactory._extract_density(cell_definition, material_id)

        CellFactory.logger.debug("Cell definition: %s ", trimmed_line)
        surfaces, cells = parse_surfaces_and_cells(trimmed_line)

        data_cards = {k: v for k, v in keyword_dict.items() if 'imp' not in k and 'ext' not in k}
        data_cards["u"] = validate_return_id_as_int(data_cards.get("u"))
        data_cards["vol"] = CellFactory._validate_volume(data_cards.get("vol", None))

        ext = CellFactory._reformat_dict_for_data_card_with_particle_designator(keyword_dict, 'ext')
        importance = CellFactory._reformat_dict_for_data_card_with_particle_designator(keyword_dict, 'imp')

        return Cell(cell_id, material_id, density, surfaces, cells, importance, data_cards, ext )

    @staticmethod
    def extract_keywords(line):
        """
        Extracts keywords and their values from the input line using regular expressions.

        Args:
            line (str): The input line to process.

        Returns:
            tuple: A tuple containing the trimmed line and a dictionary of keyword values.
        """
        pattern = re.compile(r'((?:{}))\s*=?\s*(.*?)(?={}|\Z)'.format(CellFactory.any_keyword, CellFactory.any_keyword), re.VERBOSE)
        keyword_values =  {key: value.strip() for key, value in pattern.findall(line)}
        
        # Apply re.search to each keyword and filter out None values
        matches = filter(None, map(lambda key: re.search(re.escape(key), line), keyword_values))

        # Extract match positions
        match_positions = [match.start() for match in matches]

        # Get the minimum start position or default to len(line) if no match is found
        lowest_index = min(match_positions) if match_positions else len(line)

        trimmed_line = line[:lowest_index].strip()

        return trimmed_line, keyword_values
    @staticmethod
    def _reformat_dict_for_data_card_with_particle_designator(keyword_dictionary, key):
        """
        Reformat a dictionary to include a particle designator in the key.

        Args:
            dict (dict): The dictionary to reformat.
            key (str): The particle designator to append to each key.

        Returns:
            dict: The reformatted dictionary.
        """
        result_dict = {k.strip(key).strip(":"): validate_return_id_as_int(v) for k, v in keyword_dictionary.items() if key  in k }

        return result_dict
    
    @staticmethod
    def _extract_density(line, material_id):
        """
        Extracts the density from the input line. and returns the trimmed line without density.
        Return:
            tuple: A tuple containing the trimmed line and the density value.
        """
        if material_id != 0:
            parts = line.split()
            density = float(parts[0])
            trimmed_line = " ".join(parts[1:])
            return trimmed_line, density
        
        return line, 0
    
    @staticmethod
    def _validate_volume(volume):
        """
        Validates that the volume is a number. Raises a ValueError if not.

        Args:
            volume (str): The volume value to validate.

        Returns:
            float: The validated volume as a float.

        Raises:
            ValueError: If the volume is not a valid number.
        """
        if volume is None:
            return None
        try:
            return float(volume)
        except (TypeError, ValueError):
            raise ValueError("Invalid volume value: {}".format(volume))

def parse_surfaces_and_cells(trimmed_line, separators=r"[-:()]" ):
        """
        Parses surfaces and cell exclusions from the trimmed line.

        Args:
            trimmed_line: The input line containing surface and cell information.
            separators (str): The characters to split the line by.

        Returns:
            A tuple containing:
              - A list of surfaces.
              - A list of cell exclusions.
              - An error message if an error occurred during parsing, otherwise None.
        """
        surfaces = []
        cells = []

        all_entries = re.sub(separators, " ", trimmed_line).split()
        for entry in all_entries:
                entry = entry.lstrip("0")
                if "#" in entry:
                    cells.append(validate_return_id_as_int(entry.strip("#")))
                else:
                    surfaces.append(validate_return_id_as_int(entry))
        return surfaces, cells


