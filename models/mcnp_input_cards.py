from abc import ABCMeta, abstractmethod
import re

try: 
    from npp_mcnp_plugin.utils.general_utils import validate_return_id_as_int, initialise_json_data
except ImportError:
    from utils.general_utils import validate_return_id_as_int, initialise_json_data

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
        Class method to create a Tally instance from an input line.
        """
        match = re.search(r'(\+?f)(\d+)\:?(\S+)?(.*)', line.lower())
        return cls.create_from_match(match, comment)

    @classmethod
    def create_from_match(cls, match, comment=None):
        """
        Class method to create a Tally instance from a regex match object.
        """
        if not match:
            return None
        collision_heating_enabled = "+" in match.group(1)
        tally_id = validate_return_id_as_int(match.group(2))
        tally_particles = match.group(3).split(",") if match.group(3) else None
        tally_entries = match.group(4).split() if match.group(4) else None
        
        return cls(tally_id=tally_id, particles=tally_particles, entries=tally_entries, comment=comment, collision_heating_enabled=collision_heating_enabled)

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
        Class method to create a Transformation instance from an input line.
        """
        match = re.search(r'\*?tr(\d+)(.*)', line)
        return cls.create_from_match(match, comment)

    @classmethod
    def create_from_match(cls, match, comment=None):
        """
        Class method to create a Transformation instance from a regex match object.
        """
        if not match:
            return None
        id = validate_return_id_as_int(match.group(1))
        parameters = match.group(2)
        if "*" in match.group(0)[0:2]:
            comment += " Angles transformation "
        return cls(id, parameters, comment)

class Surface(Printable):
    def __init__(self, surface_id, surface_type, parameters, comment, transformation=None):
        assert isinstance(surface_id, int), "surface_id must be an int"
        self.id = surface_id
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
        Class method to create a Surface instance from an input line.
        """
        match = re.search(r'^\d+(.*)', line)
        return cls.create_from_match(match, comment)

    @classmethod
    def create_from_match(cls, match, comment=None):
        """
        Class method to create a Surface instance from a regex match object.
        """
        if not match:
            return None
        surface_data = match.group(0).split()
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

        return cls(surface_id, surface_type, surface_params, comment, surface_transform)

class Isotope(object):
    # Class variable for element names (shared across all instances)
    element_names = initialise_json_data("element_names.json")

    def __init__(self, z, a, abundance, library=None, comment=""):
        self.z = z  # Atomic number
        self.a = a  # Mass number
        self.abundance = abundance
        self.library = library  # Optional library type, e.g., ".70c"
        self.comment = comment  # Comments specific to the isotope

    @property
    def zzzaaa(self):
        """Dynamically derive the zzzaaa code from z and a."""
        return self.z * 1000 + self.a

    @property
    def name(self):
        """Dynamically derive the element name from atomic number."""
        return self.get_element_name(self.z)

    @classmethod
    def get_element_name(cls, z):
        """Access the class variable for element names."""
        return cls.element_names.get(str(z), 'Unknown Element')

    def add_comment(self, comment):
        """Add additional information to the isotope comment."""
        self.comment += comment

    def __str__(self):
        """String representation of the isotope."""
        return "{:>4} {:>3} {:>3} {:.3e}".format(self.name, self.z, self.a, self.abundance)

class IsotopeFactory(object):
    """Singleton factory class for creating Isotope instances."""
    _instance = None
    element_names = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IsotopeFactory, cls).__new__(cls)
            cls.element_names = initialise_json_data("element_names.json")
        return cls._instance

    @classmethod
    def get_element_name(cls, z):
        return cls.element_names.get(str(z), 'Unknown Element')

    def create_isotope(self, zzzaaa, abundance, library=None):
        z = zzzaaa // 1000
        a = zzzaaa % 1000
        name = self.get_element_name(z)
        return Isotope(z, a, abundance, library)

    def create_isotope_from_input(self, zzzaaa_library, abundance_str):
        """
        Parse an input string to extract zzzaaa, library, and abundance.
        """
        # Split the string into parts; provide a default empty string for the library
        parts = zzzaaa_library.split(".")
        zzzaaa = validate_return_id_as_int(parts[0])  # Convert zzzaaa to integer
        library = parts[1] if len(parts) > 1 else None

        # Convert abundance to float
        try:
            abundance = float(abundance_str)
        except ValueError:
            raise ValueError("Abundance ({}) is not a valid number".format(abundance_str))

        # Delegate creation of the isotope
        return self.create_isotope(zzzaaa, abundance, library)

class Material(Printable):
    """Class representing a material containing multiple isotopes."""

    def __init__(self, material_id, comment, isotopes=None):
        assert isinstance(material_id, int), "material_id must be an int"
        self.id = material_id
        self.comment = comment
        self.density = None
        self.atomic_density = None
        self.isotopes = isotopes if isotopes else []

    def add_isotope(self, isotope):
        self.isotopes.append(isotope)

    def __str__(self):
        sorted_isotopes = sorted(self.isotopes, key=lambda x: abs(x.abundance), reverse=True)[:5]
        isotopes_str = "\n".join(str(iso) for iso in sorted_isotopes)
        if len(self.isotopes) > 5:
            return "Material {}\nTop 5 Isotopes:\nName   Z   A   Abundance\n{}".format(self.id, isotopes_str)
        return "Material {}\nIsotopes:\nName   Z   A   Abundance\n{}".format(self.id, isotopes_str)

    @classmethod
    def create_from_input_line(cls, line, comment=None):
        """
        Class method to create a Material instance from an input line.
        """
        match = re.search(r'm(\d+)(.*)', line)
        return cls.create_from_match(match, comment)

    @classmethod
    def create_from_match(cls, match, comment=None):
        """
        Class method to create a Material instance from a regex match object.
        """
        if not match:
            raise ValueError("Invalid material line format")
        material_id = int(match.group(1))
        material_instance = cls(material_id, comment)
        parameters = match.group(2).split()

        if len(parameters) % 2 != 0:
            raise SyntaxError("Uneven number of material entries")

        factory = IsotopeFactory()
        for i in range(0, len(parameters), 2):
            isotope = factory.create_isotope_from_input(parameters[i], parameters[i + 1])
            material_instance.add_isotope(isotope)

        return material_instance

    def print_output(self):
        if self.density is not None:
            return "%s %s" % (self.id, -self.density)
        else:
            return "%s %s" % (self.id, self.atomic_density)
        return

class Cell(object):
    """
    Represents a Cell with material, surfaces, excluded cells, and other attributes.
    """

    def __init__(self, cell_id, material_id, density, surfaces=None, cells=None, importance=None, data_cards=None, ext=None):
        """Initialize Cell object with required parameters.
    
        Args:
            cell_id (int): Unique cell identifier
            material_id (int): Material identifier (0 for void)
            density (float): Material density (-ve for g/cm3, +ve for atoms/barn-cm)
            surfaces (list, optional): List of surface identifiers
            cells (list, optional): List of cell identifiers
            importance (dict, optional): Dictionary of importance values
            data_cards (dict, optional): Dictionary of data card values
            ext (dict, optional): Dictionary of extension values
        """
        # Type validation
        assert isinstance(cell_id, int), "cell_id must be an int"
        assert isinstance(material_id, int), "material_id must be an int"
        assert isinstance(density, (int, float)), "density must be numeric"
        assert surfaces is None or isinstance(surfaces, list), "surfaces must be a list"
        assert cells is None or isinstance(cells, list), "cells must be a list"
        assert importance is None or isinstance(importance, dict), "importance must be a dict"
        assert data_cards is None or isinstance(data_cards, dict), "data_cards must be a dict"
        assert ext is None or isinstance(ext, dict), "ext must be a dict"
        
        # Assign values
        self.id = cell_id
        self.material_id = material_id
        self.density = float(density)  # Convert to float
        self.surfaces = surfaces if surfaces else []
        self.cells = cells if cells  else []
        self.importance = importance if importance is not None else {}
        self.ext = ext if ext is not None else {}
        self.data_cards = data_cards if data_cards is not None else {}

    def __str__(self):
        parts = ["Cell {}: Material ID {}".format(self.id, self.material_id)]
        
        if self.surfaces:
            parts.append("Surfaces {}".format(self.surfaces))
        if self.cells:
            parts.append("Cells {}".format(self.cells))
        if self.importance:
            parts.append("Importance {}".format(self.importance))
        if self.ext:
            parts.append("ext {}".format(self.ext))
        if self.data_cards:
            parts.append("data cards {}".format(self.data_cards))
            
        return ", ".join(parts)

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