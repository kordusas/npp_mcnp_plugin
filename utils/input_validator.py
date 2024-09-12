from npp_mcnp_plugin.models.mcnp_input_cards import Surface, Cell, Material, Transformation, Tally
from Npp import notepad
import os, json


class InputValidator(object):
    """
    Validates the input objects and returns error messages if necessary.
    """

    def __init__(self):
        self.surface_info = self.initialise_json_data('surface_info.json')
        self.particle_designators_info = self.initialise_json_data('particle_designators_info.json')

    def initialise_json_data(self, filename):
        current_dir = os.path.dirname(__file__)
        file_path = os.path.join(current_dir, '..', 'data', filename)
        with open(file_path, 'r') as json_file:
            surface_info = json.load(json_file)
        return surface_info
    def validate_cell(self, cell):
        """
        Validates a cell object and returns an error message if necessary.
        """
        if not isinstance(cell, Cell):
            return "Invalid cell object. Expected a Cell object."
        if cell.cell_id is None:
            return "Cell id is missing."
        return None

    def validate_surface(self, surface):
        """
        Validates a surface object and returns an error message if necessary.
        """
        valid_surface_types = self.surface_info.keys()

        if not isinstance(surface, Surface):
            return "Invalid surface object. Expected a Surface object."
        if surface.id is None:
            return "Surface id is missing."
        if surface.surface_type not in valid_surface_types:
            return "Surface id {} invalid surface type {}.".format(surface.id, surface.surface_type)
        return None

    def validate_transformation(self, transformation):
        """
        Validates a transformation object and returns an error message if necessary.
        """
        if not isinstance(transformation, Transformation):
            return "Invalid transformation object. Expected a Transformation object."
        if transformation.id is None:
            return "Transformation id is missing."
        if transformation.parameters is None:
            return "Transformation id {} parameters are missing.".format(transformation.id)
        return None
    def validate_tally(self, tally):
        """
        Validates a tally object and returns an error message if necessary.
        """
        if not isinstance(tally, Tally):
            return "Invalid tally object. Expected a Tally object."
        if tally.id is None:
            return "Tally id is missing."
        
        error = self._validate_tally_particles(tally)
        if error:
            return error
        
        if tally.entries is None:
            return "Tally id {} is missing cells/surfaces.".format(tally.id)
        
        return None

    def _validate_tally_particles(self, tally):
        """
        Validates the particles attribute of a tally object.
        """
        valid_particles = self.particle_designators_info.keys()
        
        if tally.particles is None:
            return "Tally id {} is missing particle designator.".format(tally.id)
        
        if isinstance(tally.particles, str):
            if tally.particles not in valid_particles:
                return "Tally id {} invalid particle designator {}.".format(tally.id, tally.particles)
        
        if isinstance(tally.particles, list):
            for particle in tally.particles:
                if particle not in valid_particles:
                    return "Tally id {} invalid particle designator {}.".format(tally.id, particle)
        return None

    def validate_material(self, material):
        """
        Validates a material object and returns an error message if necessary.
        """
        if not isinstance(material, Material):
            return "Invalid material object. Expected a Material object."
        if material.id is None:
            return "Material id is missing."
        if material.isotopes is None:
            return "Material id {} has no isotopes.".format(material.id)
        return None


