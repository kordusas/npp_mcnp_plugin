    
from Npp import editor
from information import surface_info

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

    def notify_surface_block_selected(self, analysis_result):
        """
        This function notifies the user what in a surface block has been selected.
        """
        action_type = analysis_result.get("type")
        value = analysis_result.get("value")

        # if surface type is selected we find description in the dict and popup message
        if action_type == "surface_type":
            self._popup_notification(surface_info.get(value))
        if action_type == "transformation_id":
            self._popup_notification(analysis_result["value"])

    def notify_cell_block_selected(self, analysis_result):
        """
        This function notifies the user what in a cell block has been selected.
        """
        pass

    def notify_physics_block_selected(self, analysis_result):
        """
        This function notifies the user what in a physics block has been selected.
        """
        pass

    def notify_no_block_selected(self):
        """
        This function notifies the user that no block has been selected.
        """
        pass 
    def _popup_notification(self, message):
        """
        This function checks if message is text and pops up a notification message.
        """
        if not message:
            editor.callTipShow(editor.getSelectionEnd(), "The Machine Spirit Does not Recognize this Selection")

        if isinstance(message, str):
            editor.callTipShow(editor.getSelectionEnd(), message)
        else:
            editor.callTipShow(editor.getSelectionEnd(), "wrong message type {}\n".format(type(message)))
        
            
