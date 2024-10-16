
from abc import ABCMeta, abstractmethod
from npp_mcnp_plugin.utils.string_utils import return_list_entries_starting_with_string
from npp_mcnp_plugin.utils.general_utils import format_notifier_message
import logging
import re
from Npp import editor

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
        


class SurfaceBlockAutoCompletePresenter(AbstractBlockAutoCompletePresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(SurfaceBlockAutoCompletePresenter, self).__init__(model_of_current_line, mcnp_input, notifier)

    def provide_autocomplete_suggestions(self):
        pass  # Implement your surface autocomplete logic here


class CellBlockAutoCompletePresenter(AbstractBlockAutoCompletePresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(CellBlockAutoCompletePresenter, self).__init__(model_of_current_line, mcnp_input, notifier)  


    def _autocoplete_ids(self, first_digits, my_list_of_ids):
        """
        This function provides autocomplete suggestions for  ids based on the first digits entered and list provided.
        
         Args:
            first_digits (str): The first part of the cell id.
        """
 
        possible_cell_list = return_list_entries_starting_with_string(my_list_of_ids, first_digits)
        return possible_cell_list

    def provide_autocomplete_suggestions(self):
        new_entry = self.model_of_current_line.last_entry_before_cursor
        new_entry_digits = re.sub(r'[^0-9]', '', new_entry)
        entry_length = len(new_entry_digits)
        mytype=None
        message = None
        self.logger.info("Entry added: %s", new_entry)

        if  re.match(r"trcl=\d+", new_entry):
            message = self._autocoplete_ids(first_digits=new_entry_digits, my_list_of_ids=self.mcnp_input.transformations.keys())
            mytype = "translation"

        elif re.match(r"#\d+", new_entry):
            message = self._autocoplete_ids(first_digits=new_entry_digits,my_list_of_ids=self.mcnp_input.cells.keys())
            mytype = "cell"

        elif self.model_of_current_line.is_cursor_at_material:
             message = self._autocoplete_ids(first_digits=new_entry_digits,my_list_of_ids=self.mcnp_input.materials.keys())
             mytype = "material"
        
        self.logger.info("autocoplete type Found {} ".format(mytype))
        self.logger.info("autocoplete selection {} ".format(editor.autoCGetCurrentText() )) # should show what is selected but didnt work out
        # making sure all are strings
 
        return  {"type": mytype, "value": format_notifier_message(message) , "entry_length": entry_length}
    
class PhysicsBlockAutoCompletePresenter(AbstractBlockAutoCompletePresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(PhysicsBlockAutoCompletePresenter, self).__init__(model_of_current_line, mcnp_input, notifier)

    def provide_autocomplete_suggestions(self):
        pass  # Implement your physics autocomplete logic here