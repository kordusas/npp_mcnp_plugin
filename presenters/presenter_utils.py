import logging
from selection_presenters import CellBlockPresenter, SurfaceBlockPresenter, PhysicsBlockPresenter
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


def BlockAutoCompletePresenterFactory(block_type,  model_of_current_line, mcnp_input, notifier):
    """
    This function is used to create block presenters. Depending on the block type, it creates the appropriate presenter.
    """
    
    if block_type == "surfaces":
        return SurfaceBlockAutoCompletePresenter(model_of_current_line, mcnp_input, notifier)
    elif block_type == "cells":
        return CellBlockAutoCompletePresenter(model_of_current_line, mcnp_input, notifier)
    elif block_type == "physics":
        return PhysicsBlockAutoCompletePresenter(model_of_current_line, mcnp_input, notifier)  
    else:
        logging.error("Unknown block type: %s", block_type)
        return None  


        

