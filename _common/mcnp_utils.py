

class ModelMcnpInput(object):
    def __init__(self, surfaces=None, cells=None, materials=None, tallies=None, physics=None):
        """
        Initializes the MCNP input model with optional surfaces, cells, materials, tallies, and physics components.

        :param surfaces: Optional list of surfaces or a single surface object.
        :param cells: Optional list of cells or a single cell object.
        :param materials: Optional list of materials or a single material object.
        :param tallies: Optional list of tallies or a single tally object.
        :param physics: Optional list of physics settings or a single physics object.
        """
        self.surfaces = []
        self.cells = []
        self.materials = []
        self.tallies = []
        self.physics = []
        self.add_surfaces(surfaces)
        self.add_cells(cells)
        self.add_materials(materials)
        self.add_tallies(tallies)
        self.add_physics(physics)

    def add_surfaces(self, surfaces):
        """Adds surfaces to the model."""
        if surfaces is not None:
            self.surfaces.extend(surfaces if isinstance(surfaces, list) else [surfaces])

    def add_cells(self, cells):
        """Adds cells to the model."""
        if cells is not None:
            self.cells.extend(cells if isinstance(cells, list) else [cells])

    def add_materials(self, materials):
        """Adds materials to the model."""
        if materials is not None:
            self.materials.extend(materials if isinstance(materials, list) else [materials])

    def add_tallies(self, tallies):
        """Adds tallies to the model."""
        if tallies is not None:
            self.tallies.extend(tallies if isinstance(tallies, list) else [tallies])

    def add_physics(self, physics):
        """Adds physics settings to the model."""
        if physics is not None:
            self.physics.extend(physics if isinstance(physics, list) else [physics])
    
    def get_surface(self, surface_number):
        """
        This function returns the surface with the given number.
        """
        pass
    def get_cell(self, cell_number):
        """
        This function returns the cell with the given number.
        """
        pass
    def get_material(self, material_number):
        """ 
        This function returns the material with the given number.
        """
        pass
    def get_tally(self, tally_number):
        """
        This function returns the tally with the given number.
        """
        pass
        
    def is_line_in_surface_block(self, line_number):
        """
        This function returns True if the line number is in a surface block.
        """ 
        pass    
    def is_line_in_cell_block(self, line_number):
        """
        This function returns True if the line number is in a cell block.
        """ 
        pass
    def is_line_in_physics_block(self, line_number):
        """
        This function returns True if the line number is in a physics block.
        """ 
        pass

    def return_block_type(self, line_number):
        """
        This function returns the type of block the line is in.
        """
        if self.is_line_in_surface_block(line_number):
            return "surface"
        elif self.is_line_in_cell_block(line_number):
            return "cell"
        elif self.is_line_in_physics_block(line_number):
            return "physics"
        else:
            return None 
