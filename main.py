# Model-View-Presenter approach ?
from _common import ViewOfLine
          

class ModelMcnpInput():
    """
    This is a class reperesenting the MCNP input file we are editing. 
    It enables us to obtain input properties withouth the need to keep parsing the file repeatedly.
    Has indexed input properties for easy access
    
    """
    def  __init__(self):
        pass
    
    def get_surface(self, surface_number):
        """
        This function returns the surface with the given number.
        """
        pass
    def get_cell(self, cell_number):
        """
        This function returns the cell with the given number.
        """
        pass
    def get_material(self, material_number):
        """ 
        This function returns the material with the given number.
        """
        pass
    def get_tally(self, tally_number):
        """
        This function returns the tally with the given number.
        """
        pass
        
    def is_line_in_surface_block(self, line_number):
        """
        This function returns True if the line number is in a surface block.
        """ 
        pass    
    def is_line_in_cell_block(self, line_number):
        """
        This function returns True if the line number is in a cell block.
        """ 
        pass
    def is_line_in_physics_block(self, line_number):
        """
        This function returns True if the line number is in a physics block.
        """ 
        pass

    def return_block_type(self, line_number):
        """
        This function returns the type of block the line is in.
        """
        if self.is_line_in_surface_block(line_number):
            return "surface"
        elif self.is_line_in_cell_block(line_number):
            return "cell"
        elif self.is_line_in_physics_block(line_number):
            return "physics"
        else:
            return None 



    
class file_parser():
    """
    This class parses the file and creates mcnp_input object.
    """
    def __init__(self):
            pass
    
    def create_mcnp_input(self):
        """
        This function creates the mcnp_input object. from the parsed file blocks.
        """
        mcnp_input = ModelMcnpInput()
        return mcnp_input
        
    
class selection_notifications():
    """
    This class is used to pop notifications when a block of text is selected.
    Implements Singleton pattern to ensure only one instance is used throughout the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(selection_notifications, cls).__new__(cls)
            # Put any initialization here.
        return cls._instance

    def __init__(self):
        pass

    def notify_surface_block_selected(self, message):
        """
        This function notifies the user what in a surface block has been selected.
        """
        pass

    def notify_cell_block_selected(self, message):
        """
        This function notifies the user what in a cell block has been selected.
        """
        pass

    def notify_physics_block_selected(self, message):
        """
        This function notifies the user what in a physics block has been selected.
        """
        pass

    def notify_no_block_selected(self):
        """
        This function notifies the user that no block has been selected.
        """
        pass

            


def BlockPreseterFactory(self, block_type, mcnp_input,  view_of_current_line, notifier):
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
        self.parsed_file = file_parser()
        self.parsed_file.parse_file()
        self.notifier = notifier
        self.mcnp_input = self.parsed_file.create_mcnp_input()
        
        self.debug = debug
    
    def register_callbacks(self):
        editor.clearCallbacks([SCINTILLANOTIFICATION.UPDATEUI])
        editor.callbackSync(self.on_select, [SCINTILLANOTIFICATION.UPDATEUI])
        pass
    def on_file_change(self):
        """
        if file name is changed, the file is parsed again.
        """
        self.parsed_file.parse_file()
        self.mcnp_input = self.parsed_file.create_mcnp_input()
        

    def on_select(self)
        # getting the current line and the selection in a class
        view_of_current_line = ViewOfLine()
        
        # getting the block type according to which we can select presenter
        block_type = self.mcnp_input.return_block_type(ViewOfLine.current_line_no)
        
        # block presenter can analysie the 
        block_presenter = BlockPreseterFactory(block_type, self.mcnp_input, view_of_current_line, self.notifier )
        
        
            
if __name__ == "__main__":
    handler = editorHandler(selection_notifications())
    handler.register_callbacks()
    
