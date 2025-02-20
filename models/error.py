
class ErrorModel(object):
    def __init__(self, line, message, error_code=None):
        self.line = line
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return "Error Code: {:<15}\nMessage:    {:<30}\nCard:         {:<80}\n".format(
            self.error_code if self.error_code else "N/A", 
            self.message, 
            self.line
        )


class ErrorCollection(object):
    def __init__(self):
        self.errors = None

    def add_error(self, error):
        """
        Add an error to the collection if it is not None.
        """
        if error:
            if self.errors is None:
                self.errors = [error]
            else:
                self.errors.append(error)

    def get_all_errors(self):
        return self.errors

    def is_not_empty(self):
        return self.errors is not None

    def __str__(self):
        if self.errors is None:
            return ""
        error_messages = "\n".join(str(error) for error in self.errors)
        return error_messages