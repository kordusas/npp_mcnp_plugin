from Npp import notepad, editor, console, SCINTILLANOTIFICATION, UPDATE, NOTIFICATION
import time, sys
from npp_mcnp_plugin.utils.file_parser import FileParser
from npp_mcnp_plugin.views.autocoplete_view import  AutocompleteNotification
from npp_mcnp_plugin.views.selection_view import  SelectionNotification
from npp_mcnp_plugin.views.error_view   import  ErrorView

from npp_mcnp_plugin.models.line_model import ModelOfLine
from npp_mcnp_plugin.models.error import  ErrorCollection
from npp_mcnp_plugin.models.mcnp_input  import ModelMcnpInput   
from npp_mcnp_plugin.utils.general_utils import configure_logging, get_char_from_args
from npp_mcnp_plugin.utils.string_utils import is_comment_line, is_string_empty
from npp_mcnp_plugin.utils.input_validator import InputValidator
import logging

CHAR_PERIOD = "."
CHAR_SPACE = " "
CHAR_L = "l"
CHAR_HASH = "#"
from npp_mcnp_plugin.presenters.presenter_utils import BlockPreseterFactory
from npp_mcnp_plugin.presenters.validation_presenter import validate_mcnp_model
class editorHandler:
    def __init__(self, selection_notifier, error_notifier, autocomplete_notifier):
        self.selection_notifier = selection_notifier
        self.error_notifier = error_notifier
        self.autocomplete_notifier = autocomplete_notifier
        self.logger = logging.getLogger(self.__class__.__name__)
        
        
        # initialisng parser instance from file cls method 
        self._initialise_parser_and_mcnp_input()
        
    def register_callbacks(self):
        editor.clearCallbacks([SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_select, [SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_character_added, [SCINTILLANOTIFICATION.CHARADDED])
        notepad.callback(self.on_document_saved, [NOTIFICATION.FILESAVED])
        pass
    def _initialise_parser_and_mcnp_input(self):
        """
        Parse the file and create the MCNP input instance. Validate the model after parsing.
        """
        self.logger.info("Initialising ErrorCollection")
        mcnp_error_collection = ErrorCollection()
        self.logger.info("Initialising parser and Mcnp input")
        
        # Parse the file
        self.parsed_file = FileParser.from_file(notepad.getCurrentFilename(), mcnp_error_collection)
        self.mcnp_input = ModelMcnpInput.from_file_parser(self.parsed_file)

        
        # Validate the parsed model
        validator = InputValidator()  # initialise validator
        validate_mcnp_model(self.mcnp_input, mcnp_error_collection, validator)

        # Notify the error view if there are any validation errors
        self.logger.debug("Parsing errors: %s", mcnp_error_collection)
        self.error_notifier.notify(mcnp_error_collection)

    def on_document_saved(self, args):
        self.logger.info("Document saved")
        self._initialise_parser_and_mcnp_input()
        

    def on_select(self, args):
        # if the selection arguments are not updated
        #  and the selection is not updated
        
        if  args['updated'] is False or  UPDATE.SELECTION is False:
            return 
        # getting the current line and the selection in a class
        model_of_current_line = ModelOfLine.from_notepad()
        
        # if the current line is a comment or the selection is empty or the line is empty then return
        if (is_comment_line(model_of_current_line.current_line) or 
            is_string_empty(model_of_current_line.selected_text) or 
            is_string_empty(model_of_current_line.current_line)):
            return
        
        # getting the block type according to which we can select presenter
        block_type = self.mcnp_input.return_block_type(model_of_current_line.current_line_no)
        self.logger.info("Block type is: %s", block_type)
        # block presenter can analysie the 
        block_presenter = BlockPreseterFactory(block_type, model_of_current_line= model_of_current_line, mcnp_input=self.mcnp_input, notifier=self.selection_notifier)
        block_presenter.notify_selection()
        
    def on_character_added(self, args):
            char_added = get_char_from_args(args)

            if char_added == CHAR_PERIOD:
                self.logger.info("Period character added")
                #handle_period_character()
            elif char_added != CHAR_SPACE:
                self.logger.info("None space character added")
                self.handle_non_space_character(char_added)

    def handle_non_space_character(self, char_added):
        model_of_current_line = ModelOfLine.from_notepad()
        if  model_of_current_line.is_comment_line:
            return 
        
        self.logger.info("char added in non comment line")
        #autocomplete_cell_block_logic(self.parsed_file, current_line_instance, char_added)


if __name__ == "__main__":
    configure_logging(enable_logging=True)
    selection_notifier = SelectionNotification()
    error_notifier = ErrorView()
    autocomplete_notifier = AutocompleteNotification()

    handler = editorHandler(selection_notifier, error_notifier, autocomplete_notifier)
    handler.register_callbacks()