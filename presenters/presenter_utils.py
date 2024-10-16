from abc import ABCMeta, abstractmethod
import logging
from npp_mcnp_plugin.utils.general_utils import format_notifier_message, validate_return_id_as_int, initialise_json_data, find_by_key_and_prefix
surface_info = initialise_json_data("surface_info.json")
physics_and_macrobodies_info = initialise_json_data("mcnp.tmSnippets.json")
import re

def BlockPreseterFactory(block_type,  model_of_current_line, mcnp_input, notifier):
    """
    This function is used to create block presenters. Depending on the block type, it creates the appropriate presenter.
    """
    
    if block_type == "surfaces":
        return SurfaceBlockPresenter(model_of_current_line, mcnp_input, notifier)
    elif block_type == "cells":
        return CellBlockPresenter(model_of_current_line, mcnp_input, notifier)
    elif block_type == "physics":
        return PhysicsBlockPresenter(model_of_current_line, mcnp_input, notifier)  
    else:
        logging.error("Unknown block type: %s", block_type)
        return None


class AbstractBlockSelectionPresenter(object):
    __metaclass__ = ABCMeta  # This makes it an abstract class in Python 2.7

    def __init__(self, model_of_current_line, mcnp_input, notifier):
        """
        Initialize the block presenter with the given view of the current line, MCNP input, notifier, and debug flag.

        Args:
            model_of_current_line (ViewOfCurrentLine): The view of the current line containing the selected text.
            mcnp_input (MCNPIO): The MCNP input object
            notifier (Notifier): The notifier object responsible for displaying messages to the user.
            debug (bool, optional): A flag indicating whether debugging information should be logged. Defaults to True.
        """
        self.model_of_selected_line = model_of_current_line
        self.mcnp_input = mcnp_input
        self.notifier = notifier
        self.logger = logging.getLogger(self.__class__.__name__)

    
    def notify_selection(self):
        result = self.analyze_selection()
        if result is not None:
            self.notifier.notify(result)
    @abstractmethod
    def analyze_selection(self):
        # To be implemented by subclasses
        pass

class CellBlockPresenter(AbstractBlockSelectionPresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(CellBlockPresenter, self).__init__(model_of_current_line, mcnp_input, notifier)   
    """
    This class is used to handle the selection of cell blocks of text.
    """
    def is_cell_like_but_format(self):
        """
        This function checks if the cell is in the correct format.
        """
        return "like" in self.model_of_selected_line.current_line and "but" in self.model_of_selected_line.current_line
    
    def is_cell_id_selected(self):
        """
        This function checks if the cell id is selected.
        """
        self.logger.debug("Called method is_cell_id_selected")
        first_entry_in_selection = self.model_of_selected_line.first_entry_in_selection
        first_line_entry = self.model_of_selected_line.first_entry_in_line
        # check if the cursor is further than the lenght of the first entry in the line
        if len(str(first_line_entry)) > self.model_of_selected_line.selection_end+1:
            self.logger.info("Cursor column is {}".format(self.model_of_selected_line.selection_end+1))
            self.logger.info("Cursor is further than the lenght of the first entry in the line")
            return False
        elif first_entry_in_selection.isdigit() and first_line_entry.isdigit():
            return first_entry_in_selection == first_line_entry
        return False
    
    def is_material_id_selected(self):
        """
        This function checks if the material id is selected.
        It analyses the model_of_current_line and returns True if the material is selected.
        """
        first_entry_in_selection = self.model_of_selected_line.first_entry_in_selection
        second_entry_in_current_line = self.model_of_selected_line.current_line_list[1]

        self.logger.debug("Called method is_material_id_selected")
        self.logger.info("First entry in selection: {}".format(first_entry_in_selection)) 
        self.logger.info("Second entry in current line: {}".format(second_entry_in_current_line))
        if first_entry_in_selection.isdigit() and second_entry_in_current_line.isdigit():
            return first_entry_in_selection == second_entry_in_current_line
        return False
    
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
            all_surfaces = re.sub(r"[-:()]", " ", self.model_of_selected_line.selected_text).split()
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
        if self.model_of_selected_line.is_lattice_line or self.model_of_selected_line.is_selection_after_pattern("imp"):
            self.logger.info("Ignore line")
            return True
        return False
        
    def _handle_cell_id_selected(self):
        """
        This function handles the cell id selection.
        """
        cell_id = self.model_of_selected_line.first_entry_in_selection
        cell_id = validate_return_id_as_int(cell_id)

        self.logger.debug("Cell id selected: {}".format(cell_id))
        all_cell_mentions = []
        # find all the cells which have the selected cell id mentioned in the mcnp input
        for id in self.mcnp_input.cells:
            if cell_id in self.mcnp_input.cells[id].cells:
                self.logger.debug("Found #{} in the input of cell with id  {}".format(cell_id,id ))
                all_cell_mentions.append(id)
        if all_cell_mentions:
            return {"type": "cell_id", "value": "entry #{} is present in cells with id's  {}".format(cell_id, all_cell_mentions)}
        
        return {"type": "cell_id", "value": "selected cell {}".format(cell_id)}
    
    def _handle_material_id_selected(self):
        """
        This function handles the material id selection.
        """
        material_id = self.model_of_selected_line.first_entry_in_selection
        material_id = validate_return_id_as_int(material_id)

        material = self.mcnp_input.get_material(material_id)
        message = format_notifier_message(material)
        self.logger.debug("Material id selected: {}".format(material_id))
        return {"type": "material_id", "value": message}
    
    def _handle_surfaces_selected(self):
        selected_surface_ids = self._get_all_surface_id_from_selection()
        if selected_surface_ids is None:
            return None
        self.logger.debug( "selected surfaces {}".format(selected_surface_ids))
        # find the selected surfaces in the mcnp input
        selected_surfaces = [ self.mcnp_input.get_surface(validate_return_id_as_int(surface_id)) for surface_id in selected_surface_ids  ] 
        return {"type": "surface_id", "value": format_notifier_message(selected_surfaces)}
    
    def is_cell_definition_selected(self):
        self.logger.debug( "Called method is_cell_definition_selected")
        # get second entry in the line which is material id
        material_id = validate_return_id_as_int(self.model_of_selected_line.current_line_list[1])

        # if material is not void then cell definition starts after third entry(index is 0 based)
        index_of_token = 2
        # if material is void then then cell definition starts after second entry(1ist index is 0 based
        if material_id == 0:
            self.logger.debug("Material is void")
            index_of_token = 1 
        
        cell_definition_start = self.model_of_selected_line.find_space_separated_token_end_positions(index_of_token)
        self.logger.debug( "Cell definition start: {}".format(cell_definition_start))
        self.logger.debug( "Selection end: {}".format(self.model_of_selected_line.selection_end))
        if self.model_of_selected_line.selection_start < cell_definition_start:
            self.logger.debug( "Cell definition is not selected")
            return False
        return True
    
    def analyze_selection(self):
        """
        This function analyses the cell.
        """
        self.logger.debug("\nCalled method analyze_selection\n")
        result = {}
        if self.should_ignore_selection():
            return None
        elif self.is_cell_like_but_format():
            return None        
        elif self.model_of_selected_line.is_current_line_continuation_line:
            self.logger.debug("Continuation line")
            return self._handle_surfaces_selected()
        elif self.is_material_id_selected():
            return self._handle_material_id_selected()
        elif self.is_cell_definition_selected():
            return self._handle_surfaces_selected()
        # order of cases matters, as this only checks if selection matches the first entry in the line
        elif self.is_cell_id_selected():
            return self._handle_cell_id_selected()        

        return None


class PhysicsBlockPresenter(AbstractBlockSelectionPresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(PhysicsBlockPresenter, self).__init__(model_of_current_line, mcnp_input, notifier,)    
    def analyze_selection(self):
        """
        Implement the abstract method to handle physics block selection.
        """
        # Example implementation
        pass

class SurfaceBlockPresenter(AbstractBlockSelectionPresenter):
    def __init__(self, model_of_current_line, mcnp_input, notifier):
        super(SurfaceBlockPresenter, self).__init__(model_of_current_line, mcnp_input, notifier)

    @property
    def is_selection_a_surface_type(self):
        """
        Check if the selected text represents a surface type.

        This method checks if the selected text contains any non-digit characters. If it does, it is considered
        a surface type. Otherwise, it is not.

        Returns:
            bool: True if the selected text is a surface type, False otherwise.
        """
        selected_text = self.model_of_selected_line.first_entry_in_selection
        return all(not text.isdigit() and text != "+" and text !="-" for text in selected_text)

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
        self.logger.debug( "Called method is_selection_a_transformation")
        if self.model_of_selected_line.is_current_line_continuation_line:
            return False
        elif self.model_of_selected_line.has_non_digit_chars_before_cursor:
            return False

        second_entry = self.model_of_selected_line.current_line_list[1]
        if second_entry.isdigit():
            first_selected_entry = self.model_of_selected_line.first_entry_in_selection
            return first_selected_entry == second_entry
        return False
    def _handle_surface_type_selected(self):
        """
        Handle the selected surface type.
        """
        surface_type = self.model_of_selected_line.first_entry_in_selection
        self.logger.debug("Surface type selected: {}".format(surface_type))
    
        # Try to find the surface type in surface_info first, then in physics_and_macrobodies_info
        message = surface_info.get(surface_type, None) or find_by_key_and_prefix(surface_type.lower(), physics_and_macrobodies_info, search_key_string="macrobody")
    
        if message is None:
            message = "Surface type not found..."
    
        message = format_notifier_message(message)
    
        return {"type": "surface_type", "value": message}
        
    
    def _handle_transformation_selected(self):
        """
        Handle the selected transformation.
        """
        transformation_id = self.model_of_selected_line.first_entry_in_selection.lstrip("0")
        transformation_id = validate_return_id_as_int(transformation_id)

        # here should go a logic to return the transformation instance which could be then printed by notifier for now just create transformation instance
        transformation_instance = self.mcnp_input.get_transformation(transformation_id)
        message = format_notifier_message(transformation_instance)
        self.logger.debug("transformation id selected: {}".format(transformation_id))
        return {"type": "transformation_id", "value": message}
    def analyze_selection(self):
        """
        Analyze the surface block selection
        log the result
        call notifier to pop the message
        """
        self.logger.debug( "Analyzing surface block selection")
        if self.is_selection_a_surface_type:
            return self._handle_surface_type_selected()
        
        elif self.is_selection_a_transformation:
            return self._handle_transformation_selected()
        
        return None
        


        

