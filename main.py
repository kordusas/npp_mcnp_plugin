# Model-View-Presenter approach ?

from Npp import notepad, editor, console, SCINTILLANOTIFICATION, UPDATE, NOTIFICATION
import time, sys
from _common.text_utils import ViewOfLine, FileParser, get_char_from_args
from _common.notification_utils import SelectionNotification
from _common.mcnp_utils  import ModelMcnpInput   
from _common.general_utils import log_debug
CHAR_PERIOD = "."
CHAR_SPACE = " "
CHAR_L = "l"
CHAR_HASH = "#"
from _common.presenter_utils import BlockPreseterFactory

class editorHandler:
    def __init__(self, notifier, debug=True):
        self.notifier = notifier
        self.debug = debug
        
        # initialisng parser instance from file cls method 
        self._initialise_parser_and_mcnp_input()
        
        

    def register_callbacks(self):
        editor.clearCallbacks([SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_select, [SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_character_added, [SCINTILLANOTIFICATION.CHARADDED])
        pass

    def _initialise_parser_and_mcnp_input(self):
        """
        parse the file and create the mcnp input instance.
        """
        self.parsed_file = FileParser.from_file(notepad.getCurrentFilename())
        self.mcnp_input = ModelMcnpInput.from_file_parser(self.parsed_file)
        

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
        log_debug(self.debug, "Block type is: %s\n" % block_type)   
        # block presenter can analysie the 
        block_presenter = BlockPreseterFactory(block_type, view_of_current_line= view_of_current_line, mcnp_input=self.mcnp_input, notifier=self.notifier, debug=self.debug )
        block_presenter.notify_selection()
        
    def on_character_added(self, args):
            char_added = get_char_from_args(args)

            if char_added == CHAR_PERIOD:
                log_debug(self.debug, "Period character added\n")
                #handle_period_character()
            elif char_added != CHAR_SPACE:
                # 
                log_debug(self.debug, "None space character added\n")
                self.handle_non_space_character(char_added)
    def handle_non_space_character(self, char_added):
        current_line_instance = ViewOfLine(debug=self.debug)
        if  current_line_instance.is_comment_line:
            return 
        
        log_debug(self.debug, "char added in non comment line")
        #autocomplete_cell_block_logic(self.parsed_file, current_line_instance, char_added)


if __name__ == "__main__":
    notifier = SelectionNotification()
    handler = editorHandler(notifier, debug=True)
    handler.register_callbacks()
    
