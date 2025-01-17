from autocomplete_presenter import AbstractBlockAutoCompletePresenter
import re
from Npp import editor

class AutocompleteNewCellLinePresenter(AbstractBlockAutoCompletePresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(AutocompleteNewCellLinePresenter, self).__init__(model_of_current_line, mcnp_input, notifier)
        self.editor = editor  # Add editor reference

    def provide_autocomplete_suggestions(self):
        self.logger.info("Handling autocomplete for new cell line.")
        digit_line_pattern = re.compile(r'^\s*(\d+)')
        result = {"value": None}

        # Determine the line number above the current cursor position
        line_number = self.editor.lineFromPosition(self.editor.getCurrentPos()) - 1
        while line_number >= 0:
            current_line_text = self.editor.getLine(line_number).strip().lower()
            match = digit_line_pattern.match(current_line_text)
            if match:
                previous_ID = int(match.group(1))
                next_ID = previous_ID + 1
                while next_ID in  self.mcnp_input.cells.keys():
                    next_ID += 1
                result = {"value": next_ID}
                break
            else:
                line_number -= 1

        if not result.get("value"):
            self.logger.info("No preceding digit line found.")
        else:
            self.logger.info("Next cell ID determined: %s", result["value"])

        return result