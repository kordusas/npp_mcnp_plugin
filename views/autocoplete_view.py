from Npp import editor

class AutocompleteNotification():
    """
    This class is used to pop notifications when a block of text is selected.
    Implements Singleton pattern to ensure only one instance is used throughout the application.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AutocompleteNotification, cls).__new__(cls)
        return cls._instance
    def __init__(self):
        pass
    def _popup_notification(self, message):
        editor.autoCShow(0, message)
     
    def notify(self, analysis_result):
        action_type = analysis_result.get("type")
        value = analysis_result.get("value")
        if value:
            self._popup_notification(analysis_result["value"])
