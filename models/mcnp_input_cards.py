from abc import ABCMeta, abstractmethod
from npp_mcnp_plugin.data.information import natural_abundances
from npp_mcnp_plugin.utils.general_utils import validate_return_id_as_int
import re

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
        creates transformation instance from the line
        In future may need improvement if we want to initialise the transformation with different parameters:
        cosine or angles
        """
        match = re.search(r'tr(\d+)(.*)', line)
        id = validate_return_id_as_int(match.group(1))
        parameters = match.group(2)
        # if * in line then this is angles and not cosines
        if "*" in line[0:2]:
             comment += " Angles transformation "
        return cls(id, parameters, comment)
    
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

        return cls(surface_id, surface_type, surface_params, comment, surface_transform)

        
class Isotope(object):
    # class variable for ease of access to element names
    # hand checked.
    element_names = {
    1: 'H', 2: 'He', 3: 'Li', 4: 'Be', 5: 'B', 6: 'C', 7: 'N', 8: 'O', 9: 'F', 10: 'Ne',
    11: 'Na', 12: 'Mg', 13: 'Al', 14: 'Si', 15: 'P', 16: 'S', 17: 'Cl', 18: 'Ar', 19: 'K', 20: 'Ca',
    21: 'Sc', 22: 'Ti', 23: 'V', 24: 'Cr', 25: 'Mn', 26: 'Fe', 27: 'Co', 28: 'Ni', 29: 'Cu', 30: 'Zn',
    31: 'Ga', 32: 'Ge', 33: 'As', 34: 'Se', 35: 'Br', 36: 'Kr', 37: 'Rb', 38: 'Sr', 39: 'Y', 40: 'Zr',
    41: 'Nb', 42: 'Mo', 43: 'Tc', 44: 'Ru', 45: 'Rh', 46: 'Pd', 47: 'Ag', 48: 'Cd', 49: 'In', 50: 'Sn',
    51: 'Sb', 52: 'Te', 53: 'I', 54: 'Xe', 55: 'Cs', 56: 'Ba', 57: 'La', 58: 'Ce', 59: 'Pr', 60: 'Nd',
    61: 'Pm', 62: 'Sm', 63: 'Eu', 64: 'Gd', 65: 'Tb', 66: 'Dy', 67: 'Ho', 68: 'Er', 69: 'Tm', 70: 'Yb',
    71: 'Lu', 72: 'Hf', 73: 'Ta', 74: 'W', 75: 'Re', 76: 'Os', 77: 'Ir', 78: 'Pt', 79: 'Au', 80: 'Hg',
    81: 'Tl', 82: 'Pb', 83: 'Bi', 84: 'Po', 85: 'At', 86: 'Rn', 87: 'Fr', 88: 'Ra', 89: 'Ac', 90: 'Th',
    91: 'Pa', 92: 'U', 93: 'Np', 94: 'Pu', 95: 'Am', 96: 'Cm', 97: 'Bk', 98: 'Cf', 99: 'Es', 100: 'Fm',
    101: 'Md', 102: 'No', 103: 'Lr', 104: 'Rf', 105: 'Db', 106: 'Sg', 107: 'Bh', 108: 'Hs', 109: 'Mt',
    110: 'Ds', 111: 'Rg', 112: 'Cn', 113: 'Nh', 114: 'Fl', 115: 'Mc', 116: 'Lv', 117: 'Ts', 118: 'Og'
}

    def __init__(self, name, z, a, abundance, library=None):
        self.name = name
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
        return cls(name, z, a, abundance, library)

    @classmethod
    def get_element_name(cls, z):
        # Access the class variable for element names
        return cls.element_names.get(z, 'Unknown Element')
    
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
        # Find the material id using regex and then separate the material
        match = re.search(r'm(\d+)(.*)', line)
        if not match:
            raise ValueError("Invalid material line format")
        material_id = validate_return_id_as_int(match.group(1))
        material_instance = cls(material_id, comment)
        # Separate the parameters; they are paired in zzzaaa and abundance, and from that create isotope instances
        parameters = match.group(2).split()
        if len(parameters) % 2 != 0:
            raise ValueError("uneven amount of entries for material {0}".format(material_id))
        for i in range(0, len(parameters), 2):
            # Parameters[i] need to be split using "." to get the zzzaaa before the library
            zzzaaa_list = parameters[i].split(".")
            zzzaaa = int(zzzaaa_list[0])
            library = zzzaaa_list[1] if len(zzzaaa_list) > 1 else None
            
            try:
                abundance = float(parameters[i+1])
            except ValueError:
                raise ValueError("Abundance for isotope {0} in material {1} is missing or not a valid number".format(zzzaaa, material_id))
                continue  # This continue is syntactically incorrect here as it's within the except block
            material_instance.add_isotope(Isotope.from_zzzaaa(zzzaaa, abundance, library))

        return material_instance

class Cell(object):
    """
    cell_id is int

    material is a Material object
    surfaces is a list of surface ids
    cells is a list of cell ids i need to exclude using #
    importance is a dict of particle type as str and importance value in float
    Note:
    Technically i could have the Cell as a dict object itself i think without issues.
    But it would be useful to have methods like print cell which would write the cell in the correct format. - could be cell handler 
    but i think Cell add could be very clear, then i can just sum the cells. very easy logic. 
    Maybe I could also do the same for surfaces cell.add_cell(to make union of the cells)
    cell_exclude_cell(could make expansion of the exclusion)
       union could be 
    """
    def __init__(self, cell_id, material_id, surfaces, cells, importance):
        assert isinstance(cell_id, int), "cell_id must be an int"
        assert isinstance(material_id, int), "material_id must be an int"
        assert isinstance(surfaces, list), "surfaces must be a list"
        assert isinstance(cells, list), "cells must be a list"
        assert isinstance(importance, dict), "importance must be a dict"
        self.cell_id = cell_id
        self.material_id = material_id
        self.surfaces = surfaces
        self.cells = cells
        self.importance = importance

    def __str__(self):
        return "Cell %s: Material ID %s, Surfaces %s, Cells %s, Importance %s" % (self.cell_id, self.material_id, self.surfaces, self.cells, self.importance)
    def print_output(self):
        """
        Alternative printing method for the cell object when writting mcnp_input_file
        """
        return "%s: Material ID %s, Surfaces %s, Cells %s, Importance %s" % (self.cell_id, self.print_output, self.surfaces, self.cells, self.importance)

    def replace_surface(self, old_surface_id, new_surface):
        """
        looks through the self.surface dictionary and replaces the old surface with the new surface changing the id
        """
        if old_surface_id in self.surfaces:
            # replace list entry in surfaces of old surface id with new surface id
            self.surfaces[self.surfaces.index(old_surface_id)] = new_surface.surface_id
    def replace_material(self, old_material_name, new_material):
        self.material = new_material


