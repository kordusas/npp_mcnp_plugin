import logging
import re
try: 
    from npp_mcnp_plugin.utils.general_utils import validate_return_id_as_int
    from npp_mcnp_plugin.utils.string_utils import extract_keyword_value
    from mcnp_input_cards import  Cell
except ImportError:
    from utils.general_utils import validate_return_id_as_int
    from utils.string_utils import extract_keyword_value
    from models.mcnp_input_cards import  Cell

class CellFactory:
    """
    Factory for creating and parsing Cell instances.
    """
    logger = logging.getLogger(__name__)
    @staticmethod
    def create_from_input_line(line, comment=None):
        """
        Parses an input line and creates a Cell instance.
        """
                            
        cell_definition_text = CellFactory.split_line(line)
        CellFactory.logger.debug("Cell definition: %s ", cell_definition_text)


                             

        # It extracts the following information:
        #   match.group(1) - cell_id: A unique numerical identifier for the cell.
        #   match.group(2) - mat number: The material number associated with the cell.
        #   match.group(3) - cell definition: A string containing the cell's properties 
        #                      (e.g., density, geometry).
        match = re.search(r'(\d+)\s+(\d+)\s+(\S+.*)?', cell_definition_text)

        # if cell is like but definition
        if "like" in cell_definition_text and "but" in cell_definition_text:
            return  Cell(validate_return_id_as_int( match.group(1), 0))
                             
        if not match:
            CellFactory.logger.error("Input line format is invalid: %s", line)
            raise ValueError("Input line format is invalid")

        cell_id = validate_return_id_as_int( match.group(1))
        material_id = validate_return_id_as_int(match.group(2))
        
        # extracts the density and returns trimmed line containing only the cell definition
        trimmed_line, density = CellFactory._extract_density(match.group(3), material_id)

        surfaces, cells = parse_surfaces_and_cells(trimmed_line)

        universe, volume = CellFactory._parse_universe_and_volume(line)

        # Placeholder for importance dictionary; can be extended as needed
        importance = {}  
        return Cell(cell_id, material_id, density, surfaces, cells, importance, universe, volume)

    @staticmethod
    def _extract_importance(string):
        return None
    @staticmethod
    def split_line(line):
        """
        Iteratively removes portions of the input line that start with the keywords 
        "vol", "imp", "u", "lat", "fill" and returns only the text before encountering these keywords.

        Args:
            line (str): The input line to process.

        Returns:
            str: The remaining portion of the line after removing parts with the specified keywords.
        """
        trimmed_line = line
        params = ['imp', 'vol', 'pwt', 'ext', 'fcl', 'wwn', 'dxc', 'nonu', 'pd', 'tmp', 'u', 'trcl', 'lat', 'fill', 'elpt', 'cosy', 'bflcl']

        while any(param in trimmed_line for param in params):
            for param in params:
                # Find the param in the line
                param_index = trimmed_line.find(param)
                if param_index != -1:
                    # Retain only the part before the param
                    trimmed_line = trimmed_line[:param_index].strip()
                    break  # Restart the loop after removing the param
        return trimmed_line
    @staticmethod
    def _extract_density(line, material_id):
        if material_id != 0:
            parts = line.split()
            density = float(parts[0])
            trimmed_line = " ".join(parts[1:])
            return trimmed_line, density
        
        return line, 0

    @staticmethod
    def _parse_universe_and_volume(line):
        """Extracts the universe and volume values if present."""
        universe = extract_keyword_value(line, 'u')
        universe = validate_return_id_as_int(universe) if universe else None

        volume = extract_keyword_value(line, 'vol')
        volume = float(volume) if volume else None

        return universe, volume

    
def parse_surfaces_and_cells(trimmed_line):
        """
        Parses surfaces and cell exclusions from the trimmed line.

        Args:
            trimmed_line: The input line containing surface and cell information.

        Returns:
            A tuple containing:
              - A list of surfaces.
              - A list of cell exclusions.
              - An error message if an error occurred during parsing, otherwise None.
        """
        surfaces = []
        cells = []
        all_entries = re.sub(r"[-:()]", " ", trimmed_line).split()
        for entry in all_entries:
                entry = entry.lstrip("0")  # Remove leading zeros
                if "#" in entry:
                    cells.append(validate_return_id_as_int(entry.strip("#")))
                else:
                    surfaces.append(validate_return_id_as_int(entry))
        return surfaces, cells

        
