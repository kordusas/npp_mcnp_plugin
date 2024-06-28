# Model-View-Presenter approach ?
from _common.text_utils import ViewOfLine, FileParser
from _common.notification_utils import SelectionNotification
from _common.mcnp_utils  import ModelMcnpInput   
from Npp import editor, SCINTILLANOTIFICATION
    



def BlockPreseterFactory(self, block_type,  view_of_current_line, mcnp_input, notifier):
    """
    This function is used to create block presenters. Depending on the block type, it creates the appropriate presenter.
    """
    
    if block_type == "surface":
        return SurfaceBlockPresenter(view_of_current_line, mcnp_input, notifier)
    elif block_type == "cell":
        return CellBlockPresenter(view_of_current_line, mcnp_input, notifier)
    elif block_type == "physics":
        return PhysicsBlockPresenter(view_of_current_line, mcnp_input, notifier)    


class AbstractBlockSelectionPresenter():
    """
    This class is used to handle the selection of blocks of text.
    """
    def __init__(self, view_of_current_line, mcnp_input, notifier):
        self.block_presenter = ""
        pass
    
    def notify_selection(self):
        """
        This function shows information to the user about the selection
        """
        return {"block_type": self.block_presenter, "type": "type of selection in block", "value": "value"}


class SurfaceBlockPresenter(AbstractBlockSelectionPresenter):
    """
    This class is used to handle the selection of surface blocks of text.
    """
    pass

class CellBlockPresenter(AbstractBlockSelectionPresenter):
    """
    This class is used to handle the selection of cell blocks of text.
    """
    def is_cell_like_but_format(self):
        """
        This function checks if the cell is in the correct format.
        """
        pass
    def is_cell_id_selected(self):
        """
        This function checks if the cell id is selected.
        """
        pass
    def is_material_id_selected(self):
        """
        This function checks if the material id is selected.
        It analyses the view_of_current_line and returns True if the material is selected.
        """
        pass
    def is_density_selected(self):
        """
        This function checks if the density is selected.
        It analyses the view_of_current_line and returns True if the density is selected.
        """
        pass
    def is_surface_id_selected(self):
        """
        This function checks if the surface id is selected.
        """
        pass
    def is_cell_id_in_cell_definition_selected(self):
        """
        This function checks if the cell id is selected in the cell definition.
        """
        pass
    def notify_selection(self):
        """
        This function analyses the cell.
        """
        pass

class PhysicsBlockPresenter(AbstractBlockSelectionPresenter):
    """
    This class is used to handle the selection of physics blocks of text.
    """
    pass

class editorHandler:
    def __init__(self, notifier, debug=True):
        self.notifier = notifier
        self.debug = debug
        
        # initialisng parser instance from file cls method 
        self._initialise_parser_and_mcnp_input()
        
        

    def register_callbacks(self):
        editor.clearCallbacks([SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_select, [SCINTILLANOTIFICATION.UPDATEUI])
        pass

    def _initialise_parser_and_mcnp_input(self):
        """
        parse the file and create the mcnp input instance.
        """
        self.parsed_file = FileParser.from_file(editor.getCurrentFilename())
        self.mcnp_input = self.parsed_file.create_mcnp_input()
        

    def on_select(self)
        # getting the current line and the selection in a class
        view_of_current_line = ViewOfLine()
        
        # getting the block type according to which we can select presenter
        block_type = self.mcnp_input.return_block_type(ViewOfLine.current_line_no)
        
        # block presenter can analysie the 
        block_presenter = BlockPreseterFactory(block_type, self.mcnp_input, view_of_current_line, self.notifier )
        
        
            
if __name__ == "__main__":
    notifier = SelectionNotification()
    handler = editorHandler(notifier)
    handler.register_callbacks()
    
