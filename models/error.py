
class ErrorModel(object):
    def __init__(self, line, message):
        self.line = line
        self.message = message

    def __str__(self):
        return "Line {}: {}".format(self.line, self.message)


class ErrorCollection(object):
    def __init__(self):
        self.errors = None

    def add_error(self, error):
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
        return "\n".join(str(error) for error in self.errors)