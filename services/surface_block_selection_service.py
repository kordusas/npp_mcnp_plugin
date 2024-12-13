try: 
    from npp_mcnp_plugin.services.selection_investigation_service import SelectionInvestigationService
    from npp_mcnp_plugin.utils.general_utils import validate_return_id_as_int
except ImportError:
    from selection_investigation_service import SelectionInvestigationService
    from utils.general_utils import validate_return_id_as_int
import re

class SurfaceSelectionService(SelectionInvestigationService):
    def __init__(self, selected_mcnp_card):
        """
        Initialize the cell selection service.

        Args:
            selected_mcnp_card (MCNPCard): The selected MCNP card object.
        """
        super(SurfaceSelectionService, self).__init__(selected_mcnp_card)
    
    def selection_is_a_surface_type(self):
        """
        Check if the selected text represents a surface type.

        This method checks if the selected text contains any non-digit characters. If it does, it is considered
        a surface type. Otherwise, it is not.

        Returns:
            bool: True if the selected text is a surface type, False otherwise.
        """
        selected_text = self.selected_mcnp_card.first_entry_in_selection
        return all(not text.isdigit() and text != "+" and text !="-" for text in selected_text)
    
    
    def selection_is_a_transformation(self):
        """
        Check if the selected line represents a transformation.

        it's not a transformation if:
             - line is a continuation line then 
             - there are non-digit characters before the cursor
        If the second entry in the line is a digit, and it matches the first selected entry, it's a transformation.

        Returns:
            bool: True if the selected line is a transformation, False otherwise.
        """
        self.logger.debug( "Called method is_selection_a_transformation")
        if self.selected_mcnp_card.is_current_line_continuation_line:
            return False
        elif self.selected_mcnp_card.has_non_digit_chars_before_cursor:
            return False

        second_entry = self.selected_mcnp_card.current_line_list[1]
        if second_entry.isdigit():
            first_selected_entry = self.selected_mcnp_card.first_entry_in_selection
            return first_selected_entry == second_entry
        return False    
    def get_transformation_id(self):
        transformation_id = self.selected_mcnp_card.first_entry_in_selection.lstrip("0")
        return  validate_return_id_as_int(transformation_id)
    
    def get_surface_type(self):
        return self.selected_mcnp_card.first_entry_in_selection