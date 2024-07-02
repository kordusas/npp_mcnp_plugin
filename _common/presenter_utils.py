   
def BlockPreseterFactory(block_type,  view_of_current_line, mcnp_input, notifier):
    """
    This function is used to create block presenters. Depending on the block type, it creates the appropriate presenter.
    """
    
    if block_type == "surface":
        return SurfaceBlockPresenter(view_of_current_line, mcnp_input, notifier)
    elif block_type == "cell":
        return CellBlockPresenter(view_of_current_line, mcnp_input, notifier)
    elif block_type == "physics":
        return PhysicsBlockPresenter(view_of_current_line, mcnp_input, notifier)    


class AbstractBlockSelectionPresenter():
    """
    This class is used to handle the selection of blocks of text.
    """
    def __init__(self, view_of_current_line, mcnp_input, notifier):
        self.block_presenter = ""
        pass
    
    def notify_selection(self):
        """
        This function shows information to the user about the selection
        """
        return {"block_type": self.block_presenter, "type": "type of selection in block", "value": "value"}




class CellBlockPresenter(AbstractBlockSelectionPresenter):
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
    """
    This class is used to handle the selection of physics blocks of text.
    """
    pass

class SurfaceBlockPresenter(AbstractBlockSelectionPresenter):
    """
    This class is used to handle the selection of surface blocks of text.
    """
    pass