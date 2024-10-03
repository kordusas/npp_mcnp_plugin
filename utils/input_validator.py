from npp_mcnp_plugin.models.mcnp_input_cards import Surface, Cell, Material, Transformation, Tally, Isotope
from npp_mcnp_plugin.utils.general_utils import initialise_json_data, find_by_key_and_prefix
from Npp import notepad
import os, json


class InputValidator(object):
    """
    Validates the input objects and returns error codes and messages if necessary.
    """

    def __init__(self):
        self.surface_info = initialise_json_data('surface_info.json')
        self.particle_designators_info = initialise_json_data('particle_designators_info.json')
        self.physics_and_macrobodies_info = initialise_json_data("mcnp.tmSnippets.json")

    def validate_cell(self, cell, existing_surface_ids):
        """
        Validates a cell object and returns an error code and message if necessary.
        """
        if not isinstance(cell, Cell):
            return "CELL_INVALID_OBJECT", "Invalid cell object. Expected a Cell object."
        
        invalid_surfaces = filter(lambda surface_key: surface_key not in existing_surface_ids, cell.surfaces) if cell.surfaces else None
        if invalid_surfaces:
            return "CELL_INVALID_SURFACES", "Cell ID {} invalid surface(s) {}.".format(cell.id, invalid_surfaces)
        if not cell.surfaces:
            return "CELL_NO_SURFACES", "Cell ID {} has no surfaces.".format(cell.id)
        return None, None

    def validate_surface(self, surface):
        """
        Validates a surface object and returns an error code and message if necessary.
        """
        valid_surface_types = self.surface_info.keys()

        if not isinstance(surface, Surface):
            return "SURFACE_INVALID_OBJECT", "Invalid surface object. Expected a Surface object."
        if surface.surface_type not in valid_surface_types:
            surface_info_body = find_by_key_and_prefix(surface.surface_type, self.physics_and_macrobodies_info, search_key_string="macrobody")
            if surface_info_body is None:
                return "SURFACE_INVALID_TYPE", "Surface ID {} invalid surface type {}.".format(surface.id, surface.surface_type)
        return None, None

    def validate_transformation(self, transformation):
        """
        Validates a transformation object and returns an error code and message if necessary.
        """
        if not isinstance(transformation, Transformation):
            return "TRANSFORMATION_INVALID_OBJECT", "Invalid transformation object. Expected a Transformation object."
        if transformation.parameters is None:
            return "TRANSFORMATION_MISSING_PARAMETERS", "Transformation id {} parameters are missing.".format(transformation.id)
        return None, None

    def validate_tally(self, tally):
        """
        Validates a tally object and returns an error code and message if necessary.
        """
        if not isinstance(tally, Tally):
            return "TALLY_INVALID_OBJECT", "Invalid tally object. Expected a Tally object."       

        if tally.collision_heating_enabled is False:
            error = self._validate_tally_particles(tally)
            if error:
                return error
        elif tally.particles is not None:
            return "TALLY_COLLISION_HEATING_PARTICLE_CONFLICT", "Tally id {} collision heating enabled but particles present.".format(tally.id)
        
        if tally.entries is None:
            return "TALLY_MISSING_ENTRIES", "Tally id {} is missing cells/surfaces.".format(tally.id)

        return None, None

    def _validate_tally_particles(self, tally):
        """
        Validates the particles attribute of a tally object.
        """
        valid_particles = self.particle_designators_info.keys()

        if tally.particles is None:
            return "TALLY_MISSING_PARTICLE", "Tally id {} is missing particle designator.".format(tally.id)

        if isinstance(tally.particles, str):
            if tally.particles not in valid_particles:
                return "TALLY_INVALID_PARTICLE", "Tally id {} invalid particle designator {}.".format(tally.id, tally.particles)

        if isinstance(tally.particles, list):
            for particle in tally.particles:
                if particle not in valid_particles:
                    return "TALLY_INVALID_PARTICLE", "Tally id {} invalid particle designator {}.".format(tally.id, particle)

        return None, None

    def validate_material(self, material):
        """
        Validates a material object and returns an error code and message if necessary.
        """
        if not isinstance(material, Material):
            if material == "Void":
               return None, None
            return "MATERIAL_INVALID_OBJECT", "Invalid material object. Expected a Material object."

        if material.isotopes is None:
            return "MATERIAL_MISSING_ISOTOPES", "Material ID {} has no isotopes.".format(material.id)

        for isotope in material.isotopes:
            error = self._validate_isotope(isotope)
            if error:
                return "MATERIAL_ISOTOPE_ERROR", "Material ID {}  {}".format(material.id, error)

        return None, None

    def _validate_isotope(self, isotope):
        """
        Validates an isotope and returns an error code and message if necessary.
        """
        if not isinstance(isotope, Isotope):
            return  "Invalid isotope. Expected an Isotope object."
        if isotope.name == 'Unknown Element':
            return   "Issue with isotope {}.".format(isotope.zzzaaa)

        return None

