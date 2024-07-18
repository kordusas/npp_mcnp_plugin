from Npp import notepad, editor, console, SCINTILLANOTIFICATION, UPDATE, NOTIFICATION
import time, sys
from _common.text_utils import ViewOfLine, FileParser, get_char_from_args
from _common.notification_utils import SelectionNotification, AutocompleteNotification
from _common.error_handling import ErrorView, ErrorCollection  
from _common.mcnp_utils  import ModelMcnpInput   
from _common.general_utils import configure_logging
import logging

CHAR_PERIOD = "."
CHAR_SPACE = " "
CHAR_L = "l"
CHAR_HASH = "#"
from _common.presenter_utils import BlockPreseterFactory

class editorHandler:
    def __init__(self, selection_notifier, error_notifier, autocomplete_notifier):
        self.selection_notifier = selection_notifier
        self.error_notifier = error_notifier
        self.error_collection = ErrorCollection()
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
        parse the file and create the mcnp input instance.
        """
        self.logger.info("Initialising parser and Mcnp input")

        self.parsed_file = FileParser.from_file(notepad.getCurrentFilename(), self.error_collection)
        self.mcnp_input = ModelMcnpInput.from_file_parser(self.parsed_file)
        
        self.logger.debug("Parsing errors: %s", self.error_collection)
        
        self.error_notifier.notify(self.error_collection)

    def on_document_saved(self, args):
        self.logger.info("Document saved")
        self._initialise_parser_and_mcnp_input()
        

    def on_select(self, args):
        # if the selection arguments are not updated
        #  and the selection is not updated
        
        if  args['updated'] is False or  UPDATE.SELECTION is False:
            return 
        # getting the current line and the selection in a class
        view_of_current_line = ViewOfLine()
        
        # if the current line is a comment or the selection is empty or the line is empty then return
        if view_of_current_line.is_comment_line or view_of_current_line.selection_is_empty or view_of_current_line.is_empty_line:
            return
        
        # getting the block type according to which we can select presenter
        block_type = self.mcnp_input.return_block_type(view_of_current_line.current_line_no)
        self.logger.info("Block type is: %s", block_type)
        # block presenter can analysie the 
        block_presenter = BlockPreseterFactory(block_type, view_of_current_line= view_of_current_line, mcnp_input=self.mcnp_input, notifier=self.selection_notifier)
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
        current_line_instance = ViewOfLine()
        if  current_line_instance.is_comment_line:
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