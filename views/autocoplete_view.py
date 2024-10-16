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
    
    def notify(self, analysis_result):
        """
        SCI_AUTOCSETSEPARATOR(int separatorCharacter)
        SCI_AUTOCGETSEPARATOR -> int
        These two messages set and get the separator character used to separate words in the SCI_AUTOCSHOW list. The default is the space character.
        https://www.scintilla.org/ScintillaDoc.html#SCI_AUTOCCOMPLETE
        """
        value = analysis_result.get("value")
        entry_length = analysis_result.get("entry_length", 0)
        if value:
            editor.autoCShow(entry_length, value)
