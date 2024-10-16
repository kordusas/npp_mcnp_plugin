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
    def _popup_notification(self, message):
        """
        This function checks if message is text and pops up a notification message.
        """
        if not message:
            editor.callTipShow(editor.getSelectionEnd(), "The Machine Spirit Does not Recognize this Selection")
        else:
            editor.callTipShow(editor.getSelectionEnd(), message)


    def notify(self, analysis_result):
        """
        This method is responsible for notifying the user about the selected text based on the provided analysis result.

        :param analysis_result: A dictionary containing the type and value of the selected text.
        :type analysis_result: dict

        The function first extracts the 'type' and 'value' from the 'analysis_result' dictionary. If the 'value' is not empty, it calls the '_popup_notification' method to display a notification message to the user. The message is derived from the 'value' field of the 'analysis_result' dictionary.

        :return: None
        :rtype: None
        """        
        value = analysis_result.get("value")
        if value:
            # if surface type is selected we find description in the dict and popup message
            self._popup_notification(analysis_result["value"])
