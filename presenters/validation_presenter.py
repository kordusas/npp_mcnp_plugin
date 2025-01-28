import logging
try:
    from npp_mcnp_plugin.models.error import  ErrorModel
except ImportError:
    from models.error import  ErrorModel



def validate_mcnp_model(mcnp_input, mcnp_error_collection, validator):
    """
    Validates the parsed MCNP input model by iterating over the surfaces, cells, materials, and tallies.
    Collects validation errors if any.
    """
    logging.info("Validating MCNP model")

    # Validate Surfaces
    logging.debug("Validating MCNP surfaces")
    for surface_id, surface in mcnp_input.surfaces.items():
        error_code, error_message = validator.validate_surface(surface)
        if error_message:
            mcnp_error_collection.add_error(ErrorModel(str(surface), error_message, error_code))

    # Validate Cells
    logging.debug("Validating MCNP cells")
    for cell_id, cell in mcnp_input.cells.items():
        error_code, error_message = validator.validate_cell(cell, mcnp_input.surfaces.keys())
        if error_message:
            mcnp_error_collection.add_error(ErrorModel(str(cell), error_message, error_code))

    # Validate Materials
    logging.debug("Validating MCNP materials")
    for material_name, material in mcnp_input.materials.items():
        error_code, error_message = validator.validate_material(material)
        if error_message:
            mcnp_error_collection.add_error(ErrorModel(str(material), error_message, error_code))

    # Validate Tallies
    logging.debug("Validating MCNP tallies")
    for tally_id, tally in mcnp_input.tallies.items():
        error_code, error_message = validator.validate_tally(tally)
        if error_message:
            mcnp_error_collection.add_error(ErrorModel(str(tally), error_message, error_code))

    # Check if the model has any tallies present if not add error to the collection
    if not mcnp_input.tallies:
        mcnp_error_collection.add_error(ErrorModel("Tally Block", "No tallies present in the file", "TALLY_BLOCK_EMPTY"))

    logging.info("Validation complete.")