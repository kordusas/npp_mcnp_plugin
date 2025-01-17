import re
from npp_mcnp_plugin.utils.general_utils import  validate_return_id_as_int

def is_column_at_cell_definition(model_of_current_line, cursor_or_selection_column):
        """
        Check if the cursor or selection column is at the start of a cell definition.
        Args:
        model_of_current_line (ViewOfCurrentLine): The view of the current line containing the selected text.
        cursor_or_selection_column (int): The column position of the cursor or selection.
        Returns:
        bool: True if the cursor or selection column is at the start of a cell definition, False otherwise.
        """
        # get second entry in the line which is material id
        material_id = validate_return_id_as_int(model_of_current_line.current_line_list[1])

        # if material is not void then cell definition starts after third entry(index is 0 based)
        index_of_token = 2
        # if material is void then then cell definition starts after second entry(1ist index is 0 based
        if material_id == 0:
            index_of_token = 1 

        cell_definition_start = model_of_current_line.find_space_separated_token_end_position(index_of_token)
        if cursor_or_selection_column < cell_definition_start:
            return False

        # if cursor is after letters (imp, vol etc..) we are past the cell definition
        if bool(re.search(r'[a-zA-Z]', model_of_current_line.text_till_cursor)):
            return False

        return True