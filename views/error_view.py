from Npp import notepad

class ErrorView():
    """
    This class is used to display error messages.
    Implements Singleton pattern to ensure only one instance is used throughout the application.
    """
    def __new__(cls):
        if cls._instance is None:
            cls.instance = super(ErrorView, cls).__new__(cls)
        return cls.instance
    def notify(self, error_model_instance):
        """
        This method is responsible for notifying the user about the error message.

        :param error_model_instance: An instance of the ErrorModel class containing the error message.
        :type error_message: str

        The function calls the 'notepad.messageBox' function to display the error message to the user.

        :return: None
        :rtype: None
        """
        
        title = "MCNP Input Errors"
        flags = 0  # 0 for a standard 'OK' message box

        # Display the message box
        if error_model_instance.is_not_empty():
            notepad.messageBox(str(error_model_instance), title, flags)    