from npp_mcnp_plugin.services.selection_investigation_service import SelectionInvestigationService
from npp_mcnp_plugin.utils.general_utils import validate_return_id_as_int
from npp_mcnp_plugin.models.mcnp_cell_factory import parse_surfaces_and_cells
from utils import is_column_at_cell_definition
import re

class CellSelectionService(SelectionInvestigationService):
    def __init__(self, selected_mcnp_card):
        """
        Initialize the cell selection service.

        Args:
            selected_mcnp_card (MCNPCard): The selected MCNP card object.
        """
        super(CellSelectionService, self).__init__(selected_mcnp_card)


    def get_material_id(self):
        """
        Assuming That material ID is selected Extracts and returns the material identifier from the selected text of the MCNP card.
        """
        material_id = self.selected_mcnp_card.first_entry_in_selection
        return validate_return_id_as_int(material_id)
    
    def get_selected_surfaces(self):
        """
        Extracts and returns a list of selected surface identifiers from the selected text of the MCNP card.

        Returns:
            list: A list of strings representing the surface identifiers that are numeric.
        """
        # remove the characters which are not needed which are logical operators
        selected_surfaces, selected_cells = parse_surfaces_and_cells(self.selected_mcnp_card.selected_text)
        if selected_surfaces:
            return sorted(set(selected_surfaces))
        
        self.logger.debug("No surface is selected")
        return None   

    def get_cell_id(self):
        cell_id = self.selected_mcnp_card.first_entry_in_selection

        return validate_return_id_as_int(cell_id)
        
    def is_cell_definition_selected(self):
        """
        Check if the cursor or selection column is at the start of a cell definition.

        Returns:
            bool: True if the cursor or selection column is at the start of a cell definition, False otherwise.
        """
        return is_column_at_cell_definition(self.selected_mcnp_card,self.selected_mcnp_card.selection_start )

    def is_cell_like_but_format(self):
        """
        This function checks if the cell is in the correct format.
        """
        if "like" in self.selected_mcnp_card.current_line and "but" in self.selected_mcnp_card.current_line:
          return  True
        if "like" in self.selected_mcnp_card.entry_until_selection and "but" in self.selected_mcnp_card.entry_until_selection:
          return  True
        return False
      
    def is_cell_id_selected(self):
        """
        This function checks if the cell id is selected.
        """
        self.logger.debug("Called method is_cell_id_selected")
        first_entry_in_selection = self.selected_mcnp_card.first_entry_in_selection
        first_line_entry = self.selected_mcnp_card.first_entry_in_line
        # check if the cursor is further than the lenght of the first entry in the line
        if len(str(first_line_entry)) > self.selected_mcnp_card.selection_end+1:
            self.logger.info("Cursor column is {}".format(self.selected_mcnp_card.selection_end+1))
            self.logger.info("Cursor is further than the lenght of the first entry in the line")
            return False
        elif first_entry_in_selection.isdigit() and first_line_entry.isdigit():
            return first_entry_in_selection == first_line_entry
        return False

    def is_material_id_selected(self):
        """
        This function checks if the material id is selected.
        It analyses the model_of_current_line and returns True if the material is selected.
        """
        first_entry_in_selection = self.selected_mcnp_card.first_entry_in_selection
        second_entry_in_current_line = self.selected_mcnp_card.current_line_list[1]

        self.logger.debug("Called method is_material_id_selected")
        self.logger.info("First entry in selection: {}".format(first_entry_in_selection)) 
        self.logger.info("Second entry in current line: {}".format(second_entry_in_current_line))
        if first_entry_in_selection.isdigit() and second_entry_in_current_line.isdigit():
            return first_entry_in_selection == second_entry_in_current_line
        return False

    def is_cell_id_in_cell_definition_selected(self):
        """
        This function checks if the cell id is selected in the cell definition.
        """
        indx_of_previous_char = self.selected_mcnp_card.selection_start - 1
        previous_char = self.selected_mcnp_card.current_line[indx_of_previous_char]
        self.logger.debug("character before selection {}".format(previous_char))
        if  previous_char == "#":
            return True 

        return False
    @property
    def is_lattice_line(self):
        """ This method checks if the current line is a lattice line.
            There are two possible options to check if the current line is a lattice line:
            1. If the keyword 'fill' is present in the current line and the selection start position is after the 'fill' keyword, the line is considered a lattice line.
            2. If the current line is a continuation line (starts with four spaces)  the text from the previous line(s) is prepended to the current line until a non-continuation line is encountered. If the resulting text contains the keyword 'fill', the line is considered a lattice line.
        """
        self.logger.debug("Called method is_lattice_line")
        
        if "fill" in self.selected_mcnp_card.current_line:
            fill_index = self.selected_mcnp_card.current_line.find("fill")
            if self.selected_mcnp_card.cursor_column > fill_index:
                return True
            
        # this will not work properly i need to improve this somehow
        # checking if there is keyword fill earlier
        if "fill" in self.selected_mcnp_card.full_entry:
                return True

        return False