try: 
    from npp_mcnp_plugin.services.selection_investigation_service import SelectionInvestigationService
except ImportError:
    from selection_investigation_service import SelectionInvestigationService
import re

class SurfaceSelectionService(SelectionInvestigationService):
    def __init__(self, selected_mcnp_card):
        """
        Initialize the cell selection service.

        Args:
            selected_mcnp_card (MCNPCard): The selected MCNP card object.
        """
        super(SurfaceSelectionService, self).__init__(selected_mcnp_card)
