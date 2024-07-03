from abc import ABCMeta, abstractmethod
from general_utils import log_debug
from general_utils import format_notifier_message
def BlockPreseterFactory(block_type,  view_of_current_line, mcnp_input, notifier, debug=True):
    """
    This function is used to create block presenters. Depending on the block type, it creates the appropriate presenter.
    """
    
    if block_type == "surface":
        return SurfaceBlockPresenter(view_of_current_line, mcnp_input, notifier, debug=debug)
    elif block_type == "cell":
        return CellBlockPresenter(view_of_current_line, mcnp_input, notifier, debug=debug)
    elif block_type == "physics":
        return PhysicsBlockPresenter(view_of_current_line, mcnp_input, notifier, debug=debug)    


class AbstractBlockSelectionPresenter(object):
    __metaclass__ = ABCMeta  # This makes it an abstract class in Python 2.7

    def __init__(self, view_of_current_line, mcnp_input, notifier, debug=True):
        self.view_of_selected_line = view_of_current_line
        self.mcnp_input = mcnp_input
        self.notifier = notifier
        self.debug = debug

    @abstractmethod
    def notify_selection(self):
        """
        This function shows information to the user about the selection.
        As an abstract method, it must be implemented by subclasses.
        """
        pass





class CellBlockPresenter(AbstractBlockSelectionPresenter):
    def __init__(self, view_of_current_line, mcnp_input, notifier, debug=True):
        super(CellBlockPresenter, self).__init__(view_of_current_line, mcnp_input, notifier, debug)   
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
    def __init__(self, view_of_current_line, mcnp_input, notifier, debug=True):
        super(PhysicsBlockPresenter, self).__init__(view_of_current_line, mcnp_input, notifier, debug)    
    def notify_selection(self):
        """
        Implement the abstract method to handle physics block selection.
        """
        # Example implementation
        pass

class SurfaceBlockPresenter(AbstractBlockSelectionPresenter):
    def __init__(self, view_of_current_line, mcnp_input, notifier, debug=True):
        super(SurfaceBlockPresenter, self).__init__(view_of_current_line, mcnp_input, notifier, debug)

    @property
    def is_selection_a_surface_type(self):
        """
        Check if the selected text represents a surface type.

        This method checks if the selected text contains any non-digit characters. If it does, it is considered
        a surface type. Otherwise, it is not.

        Returns:
            bool: True if the selected text is a surface type, False otherwise.
        """
        selected_text = self.view_of_selected_line.first_entry_in_selection
        return all(not text.isdigit() for text in selected_text)

    @property
    def is_selection_a_transformation(self):
        """
        Check if the selected line represents a transformation.

        it's not a transformation if:
             - line is a continuation line then 
             - there are non-digit characters before the cursor
        If the second entry in the line is a digit, and it matches the first selected entry, it's a transformation.

        Returns:
            bool: True if the selected line is a transformation, False otherwise.
        """
        log_debug(self.debug, "Called method is_selection_a_transformation\n")
        if self.view_of_selected_line.is_continuation_line:
            return False
        elif self.view_of_selected_line.has_non_digit_chars_before_cursor:
            return False

        second_entry = self.view_of_selected_line.current_line_list[1]
        if second_entry.isdigit():
            first_selected_entry = self.view_of_selected_line.first_entry_in_selection
            return first_selected_entry == second_entry
        return False

    def notify_selection(self):
        """
        Analyze the surface block selection
        log the result
        call notifier to pop the message
        """
        log_debug(self.debug, "Analyzing surface block selection\n")
        if self.is_selection_a_surface_type:
            surface_type = self.view_of_selected_line.first_entry_in_selection
            log_debug(self.debug,"Surface type selected: {}\n".format(surface_type))
            self.notifier.notify_surface_block_selected({"type": "surface_type", "value": surface_type})
        elif self.is_selection_a_transformation:
            transformation_id = self.view_of_selected_line.first_entry_in_selection.lstrip("0")
            # here should go a logic to return the transformation instance which could be then printed by notifier for now just create transformation instance
            transformation_instance = self.mcnp_input.get_transformation(transformation_id)
            message = format_notifier_message(transformation_instance)
            log_debug(self.debug,"transformation id selected: {}\n".format(transformation_id))
            self.notifier.notify_surface_block_selected({"type": "transformation_id", "value": message})
        else:
            return
        


        

        