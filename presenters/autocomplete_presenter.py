
from abc import ABCMeta, abstractmethod
from npp_mcnp_plugin.utils.string_utils import return_list_entries_starting_with_string
from npp_mcnp_plugin.utils.general_utils import format_notifier_message
from npp_mcnp_plugin.services.utils import is_column_at_cell_definition

import logging
import re
    
class AbstractBlockAutoCompletePresenter(object):
    __metaclass__ = ABCMeta

    def __init__(self, model_of_current_line, mcnp_input, notifier):
        """
        Initialize the autocomplete presenter.

        Args:
            model_of_current_line (ViewOfCurrentLine): View of the current line.
            mcnp_input (MCNPIO): The MCNP input object.
            notifier (Notifier): For displaying messages/suggestions.
        """
        self.model_of_current_line = model_of_current_line
        self.mcnp_input = mcnp_input
        self.notifier = notifier
        self.logger = logging.getLogger(self.__class__.__name__)
    def _autocoplete_ids(self, first_digits, my_list_of_ids):
        """
        This function provides autocomplete suggestions for ids based on the first digits entered and list provided.
        
         Args:
            first_digits (str): The first part of the cell id.
        """
 
        possible_cell_list = return_list_entries_starting_with_string(my_list_of_ids, first_digits)
        return possible_cell_list
    
    def pop_suggestions(self):
        result = self.provide_autocomplete_suggestions()
        if result.get("value"):
            self.logger.info("Autocompletion Trigger")
            self.notifier.notify(result)
        return result
    @abstractmethod
    def provide_autocomplete_suggestions(self):
        """
        Generate and provide autocomplete suggestions.
        """
        # for not return empty dictionary
        
class NoOpPresenter(AbstractBlockAutoCompletePresenter):
    def provide_autocomplete_suggestions(self):
        self.logger.info("NoOpPresenter: Unsupported block type or irrelevant entry encountered. No suggestions provided.")
        return {}


class SurfaceBlockAutoCompletePresenter(AbstractBlockAutoCompletePresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(SurfaceBlockAutoCompletePresenter, self).__init__(model_of_current_line, mcnp_input, notifier)

    def provide_autocomplete_suggestions(self):
        return {}  # Implement your surface autocomplete logic here


class CellBlockAutoCompletePresenter(AbstractBlockAutoCompletePresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(CellBlockAutoCompletePresenter, self).__init__(model_of_current_line, mcnp_input, notifier)  


    def provide_autocomplete_suggestions(self):
        new_entry = self.model_of_current_line.last_entry_before_cursor
        new_entry_digits = re.sub(r'[^0-9]', '', new_entry) if isinstance(new_entry, str) else '' # in case itss new line and ther eis no entry
        entry_length = len(new_entry_digits)
        mytype=None
        message = None
        self.logger.info("Entry added: %s", new_entry)

        # Define regex patterns with optional negative sign
        trcl_pattern = r"trcl=-?\d+"
        hash_pattern = r"#-?\d+"
        number_pattern = r"-?\d+$"

        if  re.match(trcl_pattern, new_entry):
            message = self._autocoplete_ids(first_digits=new_entry_digits, my_list_of_ids=self.mcnp_input.transformations.keys())
            mytype = "translation"

        elif re.match(hash_pattern, new_entry):
            message = self._autocoplete_ids(first_digits=new_entry_digits,my_list_of_ids=self.mcnp_input.cells.keys())
            mytype = "cell"

        elif self.model_of_current_line.is_cursor_at_material:
             message = self._autocoplete_ids(first_digits=new_entry_digits,my_list_of_ids=self.mcnp_input.materials.keys())
             mytype = "material"

        elif re.match(number_pattern, new_entry) and self.is_cursor_at_cell_definition():
             message = self._autocoplete_ids(first_digits=new_entry_digits,my_list_of_ids=self.mcnp_input.surfaces.keys())
             mytype = "surface"

        self.logger.info("autocoplete type Found {} ".format(mytype))
 
        return  {"type": mytype, "value": format_notifier_message(message) , "entry_length": entry_length}

    def is_cursor_at_cell_definition(self):
        return is_column_at_cell_definition(self.model_of_current_line, self.model_of_current_line.cursor_column)

    
class PhysicsBlockAutoCompletePresenter(AbstractBlockAutoCompletePresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(PhysicsBlockAutoCompletePresenter, self).__init__(model_of_current_line, mcnp_input, notifier)

    def provide_autocomplete_suggestions(self):
        return {}  # Implement your physics autocomplete logic here