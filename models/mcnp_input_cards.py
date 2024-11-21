from abc import ABCMeta, abstractmethod
try: 
    from npp_mcnp_plugin.utils.general_utils import validate_return_id_as_int, initialise_json_data
    from npp_mcnp_plugin.utils.string_utils import extract_keyword_value
except ImportError:
    from utils.general_utils import validate_return_id_as_int, initialise_json_data
    from utils.string_utils import extract_keyword_value
import re
import logging
natural_abundances = initialise_json_data("natural_abundances.json")
class Printable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def print_output(self):
        pass
    

class Tally(Printable):
    def __init__(self, tally_id, particles=None, entries=None, energies=None, comment=None, collision_heating_enabled=False):
        assert isinstance(tally_id, int), "tally_id must be an int"
        self.id = tally_id
        self.particles = particles
        self.entries = entries
        self.energies = energies
        self.comment = comment
        self.collision_heating_enabled = collision_heating_enabled

    def __str__(self):
        if self.particles:
            return "Tally %s:%s %s" % (self.id, self.particles, self.entries)
        else:
            return "Tally %s: %s" % (self.id, self.entries)
    def print_output(self):
        pass
    def add_comment(self, comment):
        """
        Tally comment is often separate keyword Fc so it is nice to have a separate method for this

        """
        self.comment = comment + "\n" + self.comment
    def add_energy_bins(self, energies):
        """
        Add energy bins to the tally instance as they are often also in a separate keyword E
        """
        self.energies = energies
    @classmethod
    def create_from_input_line(cls, line, comment=None):
        """
        Class method to create a Material instance from an input line.
        Assumes :
            the input line contains all of the information about the material. 
            input line is all lower case and no comments are present in the line.
        """        
        # Assumption: line format is "f<number>:<particles> <other entries, >"
        # Example: "f4:H,He 1 100"
        
        # Use re.search safely for tally_id and tally_particles
        # Regex pattern explanation:
        # (\+?f)    : Matches an optional '+' followed by 'f'
        # (\d+)     : Matches one or more digits (the tally number)
        # \:?        : Matches an optional colon
        # (\S+)?    : Matches one or more non-whitespace characters (optional, the particles)
        # (.*)      : Matches the rest of the line (the entries)
        match = re.search(r'(\+?f)(\d+)\:?(\S+)?(.*)', line.lower())
        
        if not match:
            return None
        if "+" in match.group(1):
            collision_heating_enabled = True
        else:
            collision_heating_enabled = False

        tally_id = validate_return_id_as_int(match.group(2))
        tally_particles = match.group(3).split(",") if match.group(3) else None
        tally_entries = match.group(4).split() if match.group(4) else None
        
        return cls(tally_id=tally_id, particles=tally_particles, entries=tally_entries, comment=comment, collision_heating_enabled=collision_heating_enabled), None
class Transformation(Printable):
    def __init__(self, transformation_id, parameters, comment=None):
        assert isinstance(transformation_id, int), "transformation_id must be an int"
        self.id = transformation_id
        self.parameters = parameters
        self.comment = comment
    def __str__(self):
        return "Transformation %s: %s" % (self.id, self.parameters)
    def print_output(self):
        return "Not Implemented"
    @classmethod
    def create_from_input_line(cls, line, comment=None):
        """
        creates transformation instance from the line
        In future may need improvement if we want to initialise the transformation with different parameters:
        cosine or angles
        """
        match = re.search(r'\*?tr(\d+)(.*)', line)
        id = validate_return_id_as_int(match.group(1))
        parameters = match.group(2)
        # if * in line then this is angles and not cosines
        if "*" in line[0:2]:
             comment += " Angles transformation "
        return cls(id, parameters, comment), None
    
# class Surface is a Printable object class that has the following attributes:    
class Surface(Printable):

    def __init__(self, surface_id, surface_type, parameters, comment, transformation=None):
        assert isinstance(surface_id, int), "surface_id must be an int"
        self.id = surface_id # int
        self.surface_type = surface_type
        self.transformation = transformation
        self.parameters = parameters
        self.comment = comment

    def update_surface(self, new_surface_id, new_parameters):
        self.id = new_surface_id
        self.parameters = new_parameters
    def update_surface_parameters(self, new_parameters):
        self.parameters = new_parameters

    def __str__(self):
        if self.transformation:
            return "Surface %s: %s %s  tr: %s" % (self.id, self.surface_type, self.parameters, self.transformation)
        else:
            return "Surface %s: %s %s " % (self.id, self.surface_type, self.parameters)
        
    def print_output(self):
        if not self.transformation:
            return "%s %s %s" % (self.id, self.surface_type, self.parameters)
        return "%s %s %s %s" % (self.id, self.transformation, self.surface_type, self.parameters)
    @classmethod
    def create_from_input_line(cls, line, comment=None):
        """
        Parses a single surface line and returns a `Surface` object.

        Args:
            line (str): The line to parse.
            comment (str): The comment associated with the surface.

        Returns:
            surface (Surface): The parsed `Surface` object.
        """
        surface_data = line.split()
        if len(surface_data) < 1:
            raise ValueError("Surface ID is missing")

        surface_id = validate_return_id_as_int(surface_data[0])
        surface_transform = None
        surface_type = None
        surface_params = ""

        if len(surface_data) >= 2:
            if surface_data[1].isdigit():
                surface_transform = surface_data[1]
                if len(surface_data) >= 3:
                    surface_type = surface_data[2]
                    surface_params = ' '.join(surface_data[3:])
            else:
                surface_type = surface_data[1]
                surface_params = ' '.join(surface_data[2:])

        return cls(surface_id, surface_type, surface_params, comment, surface_transform), None

        
class Isotope(object):
    # class variable for ease of access to element names
    # hand checked.
    element_names = initialise_json_data("element_names.json")

    def __init__(self, zzzaaa, name, z, a, abundance, library=None):
        self.name = name
        self.zzzaaa = zzzaaa
        self.z = z
        self.a = a
        self.abundance = abundance
        self.comment = ""
        self.library = library # this is optional library type like .70c .60c etc

    @classmethod
    def from_zzzaaa(cls, zzzaaa, abundance, library=None):
        z = zzzaaa / 1000
        a = zzzaaa % 1000
        name = cls.get_element_name(z)
        return cls(zzzaaa, name, z, a, abundance, library)

    @classmethod
    def get_element_name(cls, z):
        # Access the class variable for element names
        return cls.element_names.get(str(z), 'Unknown Element')
    
    def add_comment(self, comment):
        self.comment += comment
    def __str__(self):
        return "{:>4} {:>3} {:>3} {:.3e}".format(self.name, self.z, self.a, self.abundance)


class Material(Printable):
    """
    later need to fix the part where both density and atomic density can be present. this cannot be the case.
    """    

    def __init__(self, material_id, comment, isotopes=None):
        assert isinstance(material_id, int), "material_id must be an int"
        self.id = material_id
        self.comment = comment
        self.density = None
        self.atomic_density = None
        self.isotopes = isotopes if isotopes is not None else []
       
        
    def __str__(self):
        sorted_isotopes = sorted(self.isotopes, key=lambda x: abs(x.abundance), reverse=True)[:5]
        isotopes_str = '\n'.join([str(iso) for iso in sorted_isotopes])
        # if we have more than 5 isotopes show only top 5 
        if len(self.isotopes) > 5:
            return "Material {}\nTop 5 Isotopes:\nName   Z   A   Abundance\n{}".format(self.id, isotopes_str)
        return "Material {}\nIsotopes:\nName   Z   A Abundance\n{}".format(self.id, isotopes_str)
    
    def print_output(self):
        if self.density is not None:
            return "%s %s" % (self.id, -self.density)
        else:
            return "%s %s" % (self.id, self.atomic_density)
        return
    def add_isotope(self, isotope):
        self.isotopes.append(isotope)
    
    @staticmethod
    def expand_natural_abundance(isotope):
        
            
        if isotope.a == 0:
            return [
                Isotope.from_zzzaaa(zzzaaa, abundance)
                for zzzaaa, abundance in natural_abundances.get(isotope.z, [])
            ]
        return [isotope]

    def expand_isotopes(self):
        expanded_isotopes = []
        for isotope in self.isotopes:
            expanded_isotopes.extend(self.expand_natural_abundance(isotope))
        self.isotopes = expanded_isotopes

    @classmethod
    def create_from_input_line(cls, line, comment=None):
        """
        Class method to create a Material instance from an input line.
        Assumes:
            the input line contains all of the information about the material.
            input line is all lower case and no comments are present in the line.
        """
        error_message = None
        # Find the material id using regex and then separate the material
        match = re.search(r'm(\d+)(.*)', line)
        if not match:
            raise ValueError("Invalid material line format")
        material_id = validate_return_id_as_int(match.group(1))
        material_instance = cls(material_id, comment)
        # Separate the parameters; they are paired in zzzaaa and abundance, and from that create isotope instances
        parameters = match.group(2).split()
        if len(parameters) % 2 != 0:
            error_message = "Uneven amount of material entries"
            return material_instance, error_message
        
        for i in range(0, len(parameters), 2):
            # Parameters[i] need to be split using "." to get the zzzaaa before the library
            zzzaaa_list = parameters[i].split(".")
            zzzaaa = int(zzzaaa_list[0])
            library = zzzaaa_list[1] if len(zzzaaa_list) > 1 else None
            
            try:
                abundance = float(parameters[i+1])
            except ValueError:
                error_message = "Abundance ({}) for isotope {} is not valid".format(parameters[i+1], zzzaaa)
                return material_instance, error_message
                
            material_instance.add_isotope(Isotope.from_zzzaaa(zzzaaa, abundance, library))

        return material_instance, error_message

class Cell(object):
    """
    Represents a Cell with material, surfaces, excluded cells, and other attributes.
    """

    def __init__(self, cell_id, material_id, density, surfaces=None, cells=None, importance=None, universe=None, volume=None):
        assert isinstance(cell_id, int), "cell_id must be an int"
        assert isinstance(material_id, int), "material_id must be an int"
        assert isinstance(surfaces, list), "surfaces must be a list"
        assert isinstance(cells, list), "cells must be a list"
        assert isinstance(importance, dict) or importance is None, "importance must be a dict or None"
        assert isinstance(universe, (int, type(None))), "universe must be an int or None"
        assert isinstance(volume, (float, type(None))), "volume must be a float or None"
        
        self.id = cell_id
        self.material_id = material_id
        self.surfaces = surfaces if surfaces else []
        self.cells = cells if cells else []
        self.importance = importance or {}
        self.universe = universe
        self.volume = volume
        self.density = density

    def __str__(self):
        if self.universe is not None and self.volume is not None:
            return "Cell {}: Material ID {}, Surfaces {}, Cells {}, Importance {}, Universe {}, Volume {}".format(
                self.id, self.material_id, self.surfaces, self.cells, self.importance, self.universe, self.volume
            )
        
        return "Cell {}: Material ID {}, Surfaces {}, Cells {}, Importance {}".format(
            self.id, self.material_id, self.surfaces, self.cells, self.importance
        )

    def replace_surface(self, old_surface_id, new_surface_id):
        """Replaces an existing surface ID with a new one."""
        try:
            idx = self.surfaces.index(old_surface_id)
            self.surfaces[idx] = new_surface_id
        except ValueError:
            pass  # old_surface_id not found

    def replace_material(self, new_material_id):
        """Replaces the material ID with a new material."""
        assert isinstance(new_material_id, int), "new_material_id must be an int"
        self.material_id = new_material_id

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
                            
        before_alpha, after_alpha = CellFactory.split_line(line)
        CellFactory.logger.debug("Split line: %s | %s", before_alpha, after_alpha)

        
        # It extracts the following information:
        #   match.group(1) - cell_id: A unique numerical identifier for the cell.
        #   match.group(2) - mat number: The material number associated with the cell.
        #   match.group(3) - cell definition: A string containing the cell's properties 
        #                      (e.g., density, geometry).
        match = re.search(r'(\d+)\s+(\d+)\s+(\S+.*)?', before_alpha)

        if not match:
            raise ValueError("Input line format is invalid")

        cell_id = validate_return_id_as_int( match.group(1))
        material_id = validate_return_id_as_int(match.group(2))
        
        # extracts the density and returns trimmed line containing only the cell definition
        trimmed_line, density = CellFactory._extract_density(match.group(3), material_id)

        surfaces, cells, error_message = CellFactory._parse_surfaces_and_cells(trimmed_line)

        if after_alpha:
            universe, volume = CellFactory._parse_universe_and_volume(after_alpha)
        else:
            universe, volume = None, None

        # Placeholder for importance dictionary; can be extended as needed
        importance = {}  
        return Cell(cell_id, material_id, density, surfaces, cells, importance, universe, volume), error_message

    @staticmethod
    def _extract_importance(string):
        return None
    @staticmethod
    def split_line(line):
        """
        Splits the line before and after the "volimpulatfill" characters. 
        This way cell definition can be separated from the other keyword based cards within the cell
        """
        for i, char in enumerate(line):
            if char in "volimpulatfill":
                before_alpha = line[:i].strip()  # Use slicing up to i
                after_alpha = line[i:].strip()  # Use slicing from i onwards
                break
        else:  # Handle the case where no relevant character is found
            before_alpha = line.strip()
            after_alpha = ""
        return before_alpha, after_alpha
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

    @staticmethod
    def _parse_surfaces_and_cells(trimmed_line):
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
        try:
            all_entries = re.sub(r"[-:()]", " ", trimmed_line).split()
            for entry in all_entries:
                entry = entry.lstrip("0")  # Remove leading zeros
                if "#" in entry:
                    cells.append(int(entry.strip("#")))
                else:
                    surfaces.append(int(entry))
            return surfaces, cells, None
        except ValueError as e:
            error_message = "Cell entry is not a valid integer: {}".format(e)
            return surfaces, cells, error_message