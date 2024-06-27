    
from Npp import editor
class SelectionNotification():
    """
    This class is used to pop notifications when a block of text is selected.
    Implements Singleton pattern to ensure only one instance is used throughout the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SelectionNotification, cls).__new__(cls)
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