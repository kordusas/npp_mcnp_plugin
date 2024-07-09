from abc import ABCMeta, abstractmethod
from _common.information import natural_abundances

class Printable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def print_output(self):
        pass
class Tally(Printable):
    def __init__(self, tally_id, particles, entries, energies=None, comment=None):
        assert isinstance(tally_id, int), "tally_id must be an int"
        self.id = tally_id
        self.particles = particles
        self.entries = entries
        self.energies = energies
        self.comment = comment
    def __str__(self):
        return "Tally%s:%s %s" % (self.id, self.particles, self.entries)
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

class Transformation(Printable):
    def __init__(self, transformation_id, parameters, comment=None):
        assert isinstance(transformation_id, int), "transformation_id must be an int"
        self.id = transformation_id
        self.parameters = parameters
        self.comment = comment
    def __str__(self):
        return "Transformation %s: %s" % (self.transformation_id, self.parameters)

    def print_output(self):
        return "Not Implemented"
    
# class Surface is a Printable object class that has the following attributes:    
class Surface(Printable):
    ALLOWED_SURFACE_TYPES = ['box', 'rpp', 'sph', 'rcc', 'rhp', 'rec', 'trc', 'ell', 'wed', 'arb', 'px', 'py', 'pz', 'so', 's', 'sx', 'sy', 'sz', 'c/x', 'c/y', 'c/z', 'cx', 'cy', 'cz', 'k/x', 'k/y', 'k/z', 'kx', 'ky', 'kz', 'sq', 'gq', 'tx', 'ty', 'tz', 'x', 'y', 'z', 'p']

    def __init__(self, surface_id, surface_type, parameters, comment, transformation=None):
        assert isinstance(surface_id, int), "surface_id must be an int"
        self.id = surface_id # int
        self.surface_type = surface_type
        self.transformation = transformation
        self.parameters = parameters
        self.comment = comment

        if self.surface_type not in self.ALLOWED_SURFACE_TYPES:
            raise ValueError("Invalid surface type. surface type: %s are not allowed" % ', '.join(self.surface_type))

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

class Isotope(object):
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

    @staticmethod
    def get_element_name(z):
        element_names = {6: 'C', 92: 'U', 1: 'H', 2: 'He'}
        return element_names.get(z, 'Unknown Element')
    
    def add_comment(self, comment):
        self.comment += comment
    def __str__(self):
        return "{:03d} {:03d} {:.3e}".format(self.z, self.a, self.abundance)


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
        return "Material {}\nTop 5 Isotopes:\nZ   A   Abundance\n{}".format(self.id, isotopes_str)
    
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


class ModelMcnpInput(object):
    def __init__(self, surfaces=None, cells=None, materials=None, tallies=None, physics=None, block_locations=None, transformations=None):
        """
        Initializes the MCNP input model with optional surfaces, cells, materials, tallies, and physics components.

        :param surfaces: Optional dict of surfaces where the key is the surface id and the value is a Surface object for easy reference.
        :param cells: Optional dict of cells where the key is the cell id and the value is a Cell object for easy reference.
        :param materials: Optional dict of materials where the key is the material name and the value is a Material object for easy reference.
        :param tallies: Optional dict of tallies where the key is the tally id and the value is a Tally object for easy reference.
        :param physics: Optional dict of physics settings where the key is the setting name and the value is the setting value.
        """
        # add dict self.surfaces = surfaces if surfaces is not None else {}
       

        self.surfaces = surfaces
        self.cells = cells
        self.materials = materials
        self.tallies = tallies
        self.physics = physics
        self.get_transformations = transformations
        self.block_locations = block_locations

        # add default material
        self.materials[0] = "Void"

    def add_surfaces(self, surfaces):
        """Adds surfaces to the model from surface list."""
        if surfaces is not None and type(surfaces) == list:
            for surface in surfaces:
                self.add_surface(surface)
        elif surfaces is not None and type(surfaces) == dict:
            for key in surfaces:
                self.add_surface(surfaces[key])

    def add_surface(self, surface):
        """Adds surfaces to the model."""
        if surface is not None:
            self.surfaces[surface.surface_id] = surface

    def add_cells(self, cells):
        """Adds cells to the model from cell list."""
        if cells is not None and type(cells) == list:
            for cell in cells:
                self.add_cell(cell)

    def add_cell(self, cell):
        """Adds cells to the model."""
        if cell is not None:
            self.cells[cell.cell_id] = cell

    def add_materials(self, materials):
        """Adds materials to the model from material list."""
        if materials is not None and type(materials) == list:
            for material in materials:
                self.add_material(material)

    def add_material(self, material):
        """Adds materials to the model."""
        if material is not None:
            self.material[material.id] = material

    def add_tally(self, tally):
        """ add tally instance to the model tally dictionary"""
        if tally is not None:
            self.tallies[tally.id] = tally

    def add_tallies(self, tallies):
        """ add tallies to the model tallies dictionary"""
        if tallies is not None and type(tallies) == list:
            for tally in tallies:
                self.add_tally(tally)

    def add_physics(self, physics):
        """Adds physics settings to the model."""
        if physics is not None:
            self.physics = physics

    @classmethod
    def from_file_parser(cls, file_parser):
        """
        Class method to initialize the ModelMcnpInput instance from a file parser object.

        :param file_parser: An object capable of parsing MCNP input files and extracting components.
        :return: An instance of ModelMcnpInput initialized with the components extracted by the file_parser.
        """
        surfaces = file_parser.get_surfaces()
        cells = file_parser.get_cells()
        materials = file_parser.get_materials()
        tallies = file_parser.get_tallies()
        physics = file_parser.get_physics()
        block_locations = file_parser.block_locations
        transformations = file_parser.get_transformations()

        return cls(surfaces, cells, materials, tallies, physics, block_locations)

    def get_surface(self, surface_id):
        """
        This function returns the surface with the given number.
        """
        # return the surface using get method, set default to None
        return self.surfaces.get(surface_id, "Surface {}: The Machine god doesn't recognize this surface".format(surface_id))
        
    def get_cell(self, cell_id):
        """
        This function returns the cell with the given number.
        """
        pass
    def get_material(self, material_id):
        """ 
        This function returns the material with the given number.
        """
        material = Material(name="dummy material", material_id=material_id)
        return material
    
    def get_tally(self, tally_id):
        """
        This function returns the tally with the given number.
        """
        pass
    def get_transformation(self, transformation_id):
        """
        This function returns the transformation with the given number. currently  a placeholder
        """
        transformation_instance = Transformation(transformation_id, "transformation parsing not implemented yet")

        return transformation_instance
    def is_line_in_surface_block(self, line_number):
        """
        Determines if the specified line is in the surfaces block.

        Args:
            line (str): The line to check.

        Returns:
            bool: True if the line is in the surfaces block, False otherwise.
        """
        if self.block_locations['surfaces']['start'] <= line_number <= self.block_locations['surfaces']['end']:
            return True
        return False 
    
    def is_line_in_cell_block(self, line_number):
        """
        Determines if the specified line is in the cells block.

        Args:
            line (str): The line to check.

        Returns:
            bool: True if the line is in the cells block, False otherwise.
        """
        if  self.block_locations['cells']['start'] <= line_number <= self.block_locations['cells']['end']:
            return  True
        
        return False
    
    def is_line_in_physics_block(self, line_number):
        """
        Determines if the specified line is in the physics block.
        Args:
            line (str): The line to check.
        Returns:
            bool: True if the line is in the physics block, False otherwise.
        """ 
        if self.block_locations['physics']['start'] <= line_number <= self.block_locations['physics']['end']:
            return True
        return False
    
    def return_block_type(self, line_number):
        """
        This function returns the type of block the line is in.
        """
        if self.is_line_in_surface_block(line_number):
            return "surface"
        elif self.is_line_in_cell_block(line_number):
            return "cell"
        elif self.is_line_in_physics_block(line_number):
            return "physics"
        else:
            return None 


class HandlerMcnpInput(object):
    """
    The intention of this class is to modify the ModelMcnpInput object by changing the surfaces and materials in the cells as needed.
    """
    def __init__(self, model_mcnp_input):
        self.model = model_mcnp_input

    def replace_surface_in_cell_block(self, old_surface_id, new_surface):

        """
        iterate over the cell dictionarry and replace the old surface with the new surface
        """
        for cell_id in self.model.cells:
            cell = self.model.cells[cell_id]
            cell.replace_surface(old_surface_id, new_surface)

    def replace_material_in_cell_block(self, old_material_name, new_material):
        for cell in self.model.cells:
            if cell.material.name == old_material_name:
                cell.material = new_material

    def replace_surface_parameters_in_surface_block(self, old_surface_id, new_surface):
        # get the old_surface_id from model surfaces dict and replace the parameters with new_surface parameters
        # use dict get method to get the surface with old_surface_id
        self.model.surfaces.get(old_surface_id).update_surface_parameters(new_surface.parameters)


    def replace_surface_in_surface_block(self, old_surface_id, new_surface):
        """
        This replaces the surface definition in surface block changing the surface id and parameters.
        """
        self.model.surfaces.get(old_surface_id).update_surface(new_surface.surface_id, new_surface.parameters)
            

    def replace_surface(self, old_surface_id, new_surface):
        """
        This function replaces the old surface with the new surface in the model (cell block and surface block).
        """
        self.replace_surface_in_cell_block(old_surface_id, new_surface)
        self.replace_surface_in_surface_block(old_surface_id, new_surface)
    # Placeholder for additional methods
"""
if  __name__ == "__main__":
        
    # Example for model creation and modification
    model = ModelMcnpInput()
    model.add_surface(Surface(1, "box", parameters="1 2 3 4 5 6", comment="surface 1"))
    model.add_surface(Surface(2, "box", parameters="7 8 9", comment="surface 2"))
    model.add_cell(Cell(cell_id=1, material_id=1, surfaces=[1,2],cells= [],importance= 1))   
    # Print surfaces before modification
    print("Before modification:")
    for surface in model.surfaces:
        print(surface)

    # Use Handler to modify a surface
    handler = HandlerMcnpInput(model)
    handler.replace_surface(2, Surface(1, "px", parameters="4", comment="surface 3"))

    # Print surfaces after modification
    print("\nAfter modification:")
    for key in model.surfaces:
        print(model.surfaces[key])
    """