from abc import ABCMeta, abstractmethod
from general_utils import log_debug
from general_utils import format_notifier_message
from information import surface_info
import re

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
        

    
    def notify_selection(self):
        result = self.analyze_selection()
        if result is not None:
            self.notifier.notify(result)
    @abstractmethod
    def analyze_selection(self):
        # To be implemented by subclasses
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
        return "like" in self.view_of_selected_line.current_line and "but" in self.view_of_selected_line.current_line
    
    def is_cell_id_selected(self):
        """
        This function checks if the cell id is selected.
        """
        log_debug(self.debug, "Called method is_cell_id_selected\n")
        first_entry_in_selection = self.view_of_selected_line.first_entry_in_selection
        first_line_entry = self.view_of_selected_line.first_entry_in_line
        # check if the cursor is further than the lenght of the first entry in the line
        if len(str(first_line_entry)) == self.view_of_selected_line.selection_end+1:
            log_debug(self.debug, "Cursor is further than the lenght of the first entry in the line\n")
            return False
        elif first_entry_in_selection.isdigit() and first_line_entry.isdigit():
            return first_entry_in_selection == first_line_entry
        return False
    
    def is_material_id_selected(self):
        """
        This function checks if the material id is selected.
        It analyses the view_of_current_line and returns True if the material is selected.
        """
        first_entry_in_selection = self.view_of_selected_line.first_entry_in_selection
        second_entry_in_current_line = self.view_of_selected_line.current_line_list[1]

        log_debug(self.debug, "Called method is_material_id_selected\n")
        log_debug(self.debug, "First entry in selection: {}\n".format(first_entry_in_selection)) 
        log_debug(self.debug, "Second entry in current line: {}\n".format(second_entry_in_current_line))
        if first_entry_in_selection.isdigit() and second_entry_in_current_line.isdigit():
            return first_entry_in_selection == second_entry_in_current_line
        return False
    
    def is_density_selected(self):
        """
        This function checks if the density is selected.
        It analyses the view_of_current_line and returns True if the density is selected.
        """
        pass

    def is_cell_id_in_cell_definition_selected(self):
        """
        This function checks if the cell id is selected in the cell definition.
        """
        pass
    def _get_all_surface_id_from_selection(self):
            """
            parse the selected line and return all surface ids in the selection
            """
            # remove the characters which are not needed which are logical operators such as 
            all_surfaces = re.sub(r"[-:()]", " ", self.view_of_selected_line.selected_text).split()
            all_surfaces = [surface.lstrip("0") for surface in all_surfaces]
            selected_surfaces = [surface for surface in all_surfaces if surface.isdigit()]
            if selected_surfaces:
                selected_surfaces = sorted(set(selected_surfaces))
                return selected_surfaces
            return None   
    
    def should_ignore_selection(self):
        """
        This function checks if the selection should be ignored.
        """
        if self.view_of_selected_line.is_lattice_line or self.view_of_selected_line.is_selection_after_pattern("imp"):
            log_debug(self.debug, "Ignore\n")
            return True
        return False
        
    def _handle_cell_id_selected(self):
        """
        This function handles the cell id selection.
        """
        cell_id = self.view_of_selected_line.first_entry_in_selection.lstrip("0")
        log_debug(self.debug, "Cell id selected: {}\n".format(cell_id))
        return {"type": "cell_id", "value": "selected cell {}".format(cell_id)}
    
    def _handle_material_id_selected(self):
        """
        This function handles the material id selection.
        """
        material_id = self.view_of_selected_line.first_entry_in_selection.lstrip("0")
        material = self.mcnp_input.get_material(material_id)
        message = format_notifier_message(material)
        log_debug(self.debug, "Material id selected: {}\n".format(material_id))
        return {"type": "material_id", "value": message}
    
    def _handle_surfaces_selected(self):
        selected_surface_ids = self._get_all_surface_id_from_selection()
        if selected_surface_ids is None:
            return None
        log_debug(self.debug, "selected surfaces {}\n".format(selected_surface_ids))
        # find the selected surfaces in the mcnp input
        selected_surfaces = [ self.mcnp_input.get_surface(int(surface_id)) for surface_id in selected_surface_ids  ] 
        return {"type": "surface_id", "value": format_notifier_message(selected_surfaces)}
    
    def analyze_selection(self):
        """
        This function analyses the cell.
        """
        result = {}
        if self.should_ignore_selection():
            return None
        elif self.is_cell_like_but_format():
            return None        
        elif self.view_of_selected_line.is_continuation_line:
            log_debug(self.debug, "Continuation line\n")
            return self._handle_surfaces_selected()

        elif self.is_cell_id_selected():
            return self._handle_cell_id_selected()

        elif self.is_material_id_selected():
            return self._handle_material_id_selected()

        return self._handle_surfaces_selected()


class PhysicsBlockPresenter(AbstractBlockSelectionPresenter):
    def __init__(self, view_of_current_line, mcnp_input, notifier, debug=True):
        super(PhysicsBlockPresenter, self).__init__(view_of_current_line, mcnp_input, notifier, debug)    
    def analyze_selection(self):
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
    def _handle_surface_type_selected(self):
        """
        Handle the selected surface type.
        """
        surface_type = self.view_of_selected_line.first_entry_in_selection
        log_debug(self.debug, "Surface type selected: {}\n".format(surface_type))
        return {"type": "surface_type", "value": surface_info.get(surface_type, "Surface type not found...")}
    
    def _handle_transformation_selected(self):
        """
        Handle the selected transformation.
        """
        transformation_id = self.view_of_selected_line.first_entry_in_selection.lstrip("0")
        # here should go a logic to return the transformation instance which could be then printed by notifier for now just create transformation instance
        transformation_instance = self.mcnp_input.get_transformation(transformation_id)
        message = format_notifier_message(transformation_instance)
        log_debug(self.debug,"transformation id selected: {}\n".format(transformation_id))
        return {"type": "transformation_id", "value": message}
    def analyze_selection(self):
        """
        Analyze the surface block selection
        log the result
        call notifier to pop the message
        """
        log_debug(self.debug, "Analyzing surface block selection\n")
        if self.is_selection_a_surface_type:
            return self._handle_surface_type_selected()
        
        elif self.is_selection_a_transformation:
            return self._handle_transformation_selected()
        
        return None
        


        

        