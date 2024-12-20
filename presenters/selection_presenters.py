from abc import ABCMeta, abstractmethod
import logging
from npp_mcnp_plugin.utils.general_utils import format_notifier_message, validate_return_id_as_int, initialise_json_data, find_by_key_and_prefix
surface_info = initialise_json_data("surface_info.json")
physics_and_macrobodies_info = initialise_json_data("mcnp.tmSnippets.json")
import re

class AbstractBlockSelectionPresenter(object):
    __metaclass__ = ABCMeta  # This makes it an abstract class in Python 2.7

    def __init__(self, selection_service, mcnp_input, notifier):
        """
        Initialize the block presenter with the given model of the selected MCNP card, MCNP input, and notifier.

        Args:
            selection_service: the selection service which contains the selected mcnp input card and can provide information about it
            mcnp_input: The MCNP input object containing the data to be processed.
            notifier: The notifier object responsible for displaying messages to the user.

        Returns:
            None
        """
        self.selected_card_service = selection_service
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
    def __init__(self, cell_selection_service, mcnp_input, notifier):
        super(CellBlockPresenter, self).__init__(cell_selection_service, mcnp_input, notifier)   
    """
    This class is used to handle the selection of cell blocks of text.
    """
    def _get_all_surface_id_from_selection(self):
            """
            match the selected surface list
            """ 
            selected_surfaces = self.selected_card_service.get_selected_surfaces()
            if selected_surfaces:
                selected_surfaces = sorted(set(selected_surfaces))
                return selected_surfaces
            self.logger.debug("No surface is selected")
            return None   

    def should_ignore_selection(self):
        """
        This function checks if the selection should be ignored.
        currently we do nothing if this is a lattice line.
        """
        if self.selected_card_service.is_lattice_line:
            self.logger.info("Ignore line")
            return True
        return False

    def _handle_cell_id_selected(self):
        """
        This function handles the cell id selection.
        """
        cell_id = self.selected_card_service.get_cell_id()

        self.logger.debug("Cell id selected: {}".format(cell_id))
        all_cell_mentions = []
        # find all the cells which have the selected cell id mentioned in the mcnp input
        for id in self.mcnp_input.cells:
            if cell_id in self.mcnp_input.cells[id].cells:
                self.logger.debug("Found #{} in the input of cell with id  {}".format(cell_id,id ))
                all_cell_mentions.append(id)

        if all_cell_mentions:
            return {"type": "cell_id", "value": "entry #{} is present in cells with id's  {}".format(cell_id, all_cell_mentions)}

        return None

    def _handle_material_id_selected(self):
        """
        This function handles the material id selection.
        """
        material_id = self.selected_card_service.get_material_id()
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

    def analyze_selection(self):
        """
        This function analyses the cell.
        """
        self.logger.debug("Called method analyze_selection\n")

        if self.should_ignore_selection():
            return None
        elif self.selected_card_service.is_cell_like_but_format():
            return None        
        elif self.selected_card_service.selected_mcnp_card.is_current_line_continuation_line:
            self.logger.debug("Continuation line")
            return self._handle_surfaces_selected()
        elif self.selected_card_service.is_material_id_selected():
            return self._handle_material_id_selected()
        elif self.selected_card_service.is_cell_definition_selected():
            if  self.selected_card_service.is_cell_id_in_cell_definition_selected():
                self.logger.debug("cell_id_in_cell_definition_selected")
                return None
            return self._handle_surfaces_selected()
        # order of cases matters, as this only checks if selection matches the first entry in the line
        elif self.selected_card_service.is_cell_id_selected():
            return self._handle_cell_id_selected()        

        self.logger.debug("Selection did not match any conditions, returning None")
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

    def _handle_surface_type_selected(self):
        """
        Handle the selected surface type.
        """
        surface_type = self.selected_card_service.get_surface_type() 
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
        
        transformation_id = self.selected_card_service.get_transformation_id()
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
        if self.selected_card_service.selection_is_a_surface_type():
            return self._handle_surface_type_selected()

        elif self.selected_card_service.selection_is_a_transformation():
            return self._handle_transformation_selected()

        return None