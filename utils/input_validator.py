from npp_mcnp_plugin.models.mcnp_input_cards import Surface, Cell, Material, Transformation, Tally
from Npp import notepad


class InputValidator(object):
    """
    Validates the input objects and returns error messages if necessary.
    """

    def __init__(self):
        pass

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
        valid_surface_types = ['box', 'rpp', 'sph', 'rcc', 'rhp', 'rec', 'trc', 'ell', 'wed', 'arb', 'px', 'py', 'pz', 'so', 's', 'sx', 'sy', 'sz', 'c/x', 'c/y', 'c/z', 'cx', 'cy', 'cz', 'k/x', 'k/y', 'k/z', 'kx', 'ky', 'kz', 'sq', 'gq', 'tx', 'ty', 'tz', 'x', 'y', 'z', 'p']

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
        if tally.particles is None:
            return "Tally id {} is missing particle designator.".format(tally.id)
        if tally.entries is None:
            return "Tally id {} is missing cells/surfaces.".format(tally.id)
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


