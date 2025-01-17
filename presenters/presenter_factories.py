import logging
from selection_presenters import CellBlockPresenter, SurfaceBlockPresenter, PhysicsBlockPresenter
from autocomplete_presenter import SurfaceBlockAutoCompletePresenter, CellBlockAutoCompletePresenter, PhysicsBlockAutoCompletePresenter, NoOpPresenter
from autocomplete_presenter_genai import AutocompleteNewCellLinePresenter
from npp_mcnp_plugin.services.cell_block_selection_service import CellSelectionService
from npp_mcnp_plugin.services.surface_block_selection_service import SurfaceSelectionService
from npp_mcnp_plugin.services.physics_block_selection_service import PhysicsSelectionService

def BlockPreseterFactory(block_type,  model_of_mcnp_card, mcnp_input, notifier):
    """
    This function is used to create block presenters. Depending on the block type, it creates the appropriate presenter and service to assist presenter.
    """
    
    if block_type == "surfaces":
        surface_selection_service = SurfaceSelectionService(model_of_mcnp_card)
        return SurfaceBlockPresenter(surface_selection_service, mcnp_input, notifier)
    elif block_type == "cells":
        cell_selection_service = CellSelectionService(model_of_mcnp_card)
        return CellBlockPresenter(cell_selection_service, mcnp_input, notifier)
    elif block_type == "physics":
        physics_selection_service = PhysicsSelectionService(model_of_mcnp_card)
        return PhysicsBlockPresenter(physics_selection_service, mcnp_input, notifier)  
    else:
        logging.error("Unknown block type: %s", block_type)
        return None


def BlockAutoCompletePresenterFactory(block_type, character_added, model_of_mcnp_card, mcnp_input, notifier):
    """
    Factory function to create appropriate autocomplete presenters based on block type and character added.

    Args:
        block_type (str): The type of block (e.g., 'surfaces', 'cells', 'physics').
        character_added (str): The character that was added (e.g., '\n', 'a', '3').
        model_of_mcnp_card (ModelOfLine): The current line model.
        mcnp_input (MCNPIO): The MCNP input object.
        notifier (Notifier): For displaying messages/suggestions.

    Returns:
        AbstractBlockAutoCompletePresenter: An instance of a presenter or None.
    """
    if character_added == '\n':
        return AutocompleteNewCellLinePresenter(model_of_mcnp_card, mcnp_input, notifier)
    elif block_type == "surfaces":
        return SurfaceBlockAutoCompletePresenter(model_of_mcnp_card, mcnp_input, notifier)
    elif block_type == "cells":
        return CellBlockAutoCompletePresenter(model_of_mcnp_card, mcnp_input, notifier)
    elif block_type == "physics":
        return PhysicsBlockAutoCompletePresenter(model_of_mcnp_card, mcnp_input, notifier)  
    else:
        logging.error("Unknown block type: %s", block_type)
        return NoOpPresenter(notifier)  # Define a NoOpPresenter that does nothing



        

