from Npp import notepad, editor, console, SCINTILLANOTIFICATION, UPDATE, NOTIFICATION
import logging

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

from npp_mcnp_plugin.presenters.presenter_utils import BlockPreseterFactory, BlockAutoCompletePresenterFactory
from npp_mcnp_plugin.presenters.validation_presenter import validate_mcnp_model
from npp_mcnp_plugin.utils.string_utils import get_block_type_from_line
CHAR_PERIOD = "."
CHAR_SPACE = " "
FILE_TYPES_TO_IGNORE = [
    # Documentation and text files
    ".txt",    # Plain text files
    ".doc",    # Microsoft Word files
    ".docx",   # Microsoft Word (modern)
    ".pdf",    # PDF files
    ".md",     # Markdown files
    ".rst",    # reStructuredText files

    # Data and log files
    ".csv",    # Comma-separated values
    ".tsv",    # Tab-separated values
    ".dat",    # Generic data files
    ".json",   # JSON files
    ".xml",    # XML files
    ".yaml",   # YAML files
    ".yml",    # YAML (alternate extension)
    ".log",    # Log files
    ".out",    # Output files
    ".tmp",    # Temporary files

    # Source code and scripts (non-MCNP relevant)
    ".py",     # Python files
    ".java",   # Java files
    ".js",     # JavaScript files
    ".c",      # C language files
    ".cpp",    # C++ files
    ".cc",     # Alternate C++ files
    ".h",      # C/C++ header files
    ".hpp",    # C++ header files
    ".f",      # Fortran files (fixed form)
    ".f90",    # Fortran files (free form)
    ".f95",    # Fortran 95 files
    ".for",    # Fortran alternate extension
    ".csh",    # C-shell scripts
    ".sh",     # Shell scripts

    # Compressed and backup files
    ".bak",    # Backup files
    ".swp",    # Swap files
    ".zip",    # Compressed archive
    ".tar",    # Tarball archive
    ".gz"      # Gzipped files
]



class EditorHandler:
    def __init__(self, selection_notifier, error_notifier, autocomplete_notifier):
        self.selection_notifier = selection_notifier
        self.error_notifier = error_notifier
        self.autocomplete_notifier = autocomplete_notifier
        self.logger = logging.getLogger(self.__class__.__name__)
        self.autocompletion_data = None

        # initialisng parser instance from file cls method 
        self._initialise_parser_and_mcnp_input()
        
    def register_callbacks(self):
        editor.clearCallbacks([SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_select, [SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_character_added, [SCINTILLANOTIFICATION.CHARADDED])
        notepad.callback(self.on_document_saved, [NOTIFICATION.FILESAVED])
        editor.callback(self.on_autocompletion_selection, [SCINTILLANOTIFICATION.AUTOCSELECTIONCHANGE])

        pass
    def _initialise_parser_and_mcnp_input(self):
        """
        Parse the file and create the MCNP input instance. Validate the model after parsing.
        """
        self.logger.info("Initialising ErrorCollection")
        mcnp_error_collection = ErrorCollection()
        self.logger.info("Initialising parser and Mcnp input")
        
        # Parse the file

        current_filename = notepad.getCurrentFilename()

        # Ignore certain file types, such as text, output, csv, or python files and stop parsing in that case
        if any(current_filename.lower().endswith(filetype.lower()) for filetype in FILE_TYPES_TO_IGNORE):
            self.logger.info("Ignoring file: {}".format(current_filename))
            return

        self.parsed_file = FileParser.from_file(current_filename, mcnp_error_collection)
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
        # if file has changed reload!
        if str(notepad.getCurrentFilename()) != self.parsed_file.filename:
            self._initialise_parser_and_mcnp_input()
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
        block_type = get_block_type_from_line(self.logger, model_of_current_line.full_entry.strip())
        self.logger.info("Block type is: %s", block_type)
        if not block_type:
             return 
        
        # block presenter can analysie the 
        block_presenter = BlockPreseterFactory(block_type, model_of_mcnp_card= model_of_current_line, mcnp_input=self.mcnp_input, notifier=self.selection_notifier)
        block_presenter.notify_selection()
        
    def on_character_added(self, args):
            char_added = get_char_from_args(args)
            model_of_current_line = ModelOfLine.from_notepad()
                
            if (char_added.isdigit() or char_added == "#") and not is_comment_line(model_of_current_line.current_line):
                self.logger.info("None space character added ")
                self.handle_character(model_of_current_line)
    def handle_character(self, model_of_current_line): 
 
        self.logger.info("char added in non comment line")

        block_type = block_type = get_block_type_from_line(self.logger, model_of_current_line.full_entry.strip())
        self.logger.info("Block type is: %s", block_type)
        if not block_type:
            return 
                
        

        # *** Create and use the Autocomplete Presenter ***
        autocomplete_presenter = BlockAutoCompletePresenterFactory(
            block_type, 
            model_of_mcnp_card=model_of_current_line, 
            mcnp_input=self.mcnp_input, 
            notifier=self.autocomplete_notifier
        )
        self.autocompletion_data = autocomplete_presenter.pop_suggestions() 
        
    def on_autocompletion_selection(self, selection):
        """
        This function is triggered when the user selects an item in the autocompletion list.
        """

        if not self.autocompletion_data:
            return
        selected_text = editor.autoCGetCurrentText()

        if selected_text:
            # Look up the selected text in the autocompletion data dictionary
            metadata = self.autocompletion_data.get("type", None)

            if metadata=="material" or metadata=="surface":
                # Print the selected item along with its type and info
                self.logger.info("Type of selection: {}, selected text: {} ".format(metadata, selected_text))

if __name__ == "__main__":
    configure_logging(enable_logging=True)

    selection_notifier = SelectionNotification()
    error_view = ErrorView()
    autocomplete_notifier = AutocompleteNotification()

    # Setting autocomplete separator as a new line character
    editor.autoCSetSeparator(ord("\n"))

    # Renamed the handler for consistency and clarity
    editor_handler = EditorHandler(selection_notifier, error_view, autocomplete_notifier)
    editor_handler.register_callbacks()
