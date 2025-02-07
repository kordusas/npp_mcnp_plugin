from Npp import notepad, editor, console, SCINTILLANOTIFICATION, UPDATE, NOTIFICATION
import logging, time, re
from npp_mcnp_plugin.utils.file_parser import FileParser
from npp_mcnp_plugin.views.autocoplete_view import  AutocompleteNotification
from npp_mcnp_plugin.views.selection_view import  SelectionNotification
from npp_mcnp_plugin.views.error_view   import  ErrorView

from npp_mcnp_plugin.models.line_model import ModelOfLine
from npp_mcnp_plugin.models.error import  ErrorCollection
from npp_mcnp_plugin.models.mcnp_input  import ModelMcnpInput   
from npp_mcnp_plugin.utils.general_utils import configure_logging, get_char_from_args, validate_return_id_as_int
from npp_mcnp_plugin.utils.string_utils import is_comment_line, is_string_empty
from npp_mcnp_plugin.utils.input_validator import InputValidator

from npp_mcnp_plugin.presenters.presenter_factories import BlockPreseterFactory, BlockAutoCompletePresenterFactory
from npp_mcnp_plugin.presenters.validation_presenter import validate_mcnp_model
from npp_mcnp_plugin.utils.string_utils import get_block_type_from_line

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
             block_type = self.mcnp_input.return_block_type(model_of_current_line.current_line_no)
             self.logger.info("Using Backup, Block type is: %s", block_type)
        
        # block presenter can analysie the 
        block_presenter = BlockPreseterFactory(block_type, model_of_mcnp_card= model_of_current_line, mcnp_input=self.mcnp_input, notifier=self.selection_notifier)
        block_presenter.notify_selection()
        
    def on_character_added(self, args):
            char_added = get_char_from_args(args)
            
            model_of_current_line = ModelOfLine.from_notepad()

            block_type = get_block_type_from_line(self.logger, model_of_current_line.full_entry.strip())
            self.logger.info("Block type is: %s, char added is: %s", block_type, char_added)
            if not block_type:
                block_type = self.mcnp_input.return_block_type(model_of_current_line.current_line_no)
                self.logger.info("Using Backup, Block type is: %s", block_type)
            
            # Delegate handling to the Presenter Factory, including editor reference and genai_service
            autocomplete_presenter = BlockAutoCompletePresenterFactory(
                block_type=block_type, 
                character_added=char_added, 
                model_of_mcnp_card=model_of_current_line, 
                mcnp_input=self.mcnp_input, 
                notifier=self.autocomplete_notifier,
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
                # get the selected item from the mcnp_input and pass to the selection_notifier to notify
                selected_item = self.mcnp_input.get_item_by_name(metadata, validate_return_id_as_int(selected_text))
                self.logger.info("Selected {} ".format(selected_item))
                #analysis_result = {"value" : selected_item}
                #self.selection_notifier.notify(analysis_result)



if __name__ == "__main__":
    configure_logging(enable_logging=True)
    
    # Record the start time
    start_time = time.time()
    
    # Initialize objects
    selection_notifier = SelectionNotification()
    error_view = ErrorView()
    autocomplete_notifier = AutocompleteNotification()
    
    # Setting autocomplete separator as a new line character
    editor.autoCSetSeparator(ord("\n"))
    
    # Renamed the handler for consistency and clarity
    editor_handler = EditorHandler(selection_notifier, error_view, autocomplete_notifier)
    editor_handler.register_callbacks()
    
    # Record the end time
    end_time = time.time()
    
    # Calculate and print the elapsed time
    elapsed_time = end_time - start_time
    editor_handler.logger.info("Initialization took {:.4e} seconds".format(elapsed_time))

