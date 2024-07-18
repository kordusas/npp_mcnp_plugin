from mcnp_utils import Surface, Cell, Material, Transformation, Tally
from Npp import notepad

class ErrorModel(object):
    def __init__(self, line, message):
        self.line = line
        self.message = message

    def __str__(self):
        return "Line {}: {}".format(self.line, self.message)

class ErrorCollection(object):
    def __init__(self):
        self.errors = None

    def add_error(self, error):
        if self.errors is None:
            self.errors = [error]
        else:
            self.errors.append(error)

    def get_all_errors(self):
        return self.errors
    def is_not_empty(self):
        return self.errors is not None
    def __str__(self):
        if self.errors is None:
            return ""
        return "\n".join(str(error) for error in self.errors)

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


class ErrorView():
    """
    This class is used to display error messages.
    Implements Singleton pattern to ensure only one instance is used throughout the application.
    """
    def __new__(cls):
        if cls._instance is None:
            cls.instance = super(ErrorView, cls).__new__(cls)
        return cls.instance
    def notify(self, error_model_instance):
        """
        This method is responsible for notifying the user about the error message.

        :param error_model_instance: An instance of the ErrorModel class containing the error message.
        :type error_message: str

        The function calls the 'notepad.messageBox' function to display the error message to the user.

        :return: None
        :rtype: None
        """
        
        title = "MCNP Input Errors"
        flags = 0  # 0 for a standard 'OK' message box

        # Display the message box
        if error_model_instance.is_not_empty():
            notepad.messageBox(str(error_model_instance), title, flags)    