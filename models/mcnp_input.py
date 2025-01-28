class ModelMcnpInput(object):
    def __init__(self, surfaces=None, cells=None, materials=None, tallies=None, physics=None, block_locations=None, transformations=None):
        """
        Initializes the MCNP input model with optional surfaces, cells, materials, tallies, and physics components.

        :param surfaces: Optional dict of surfaces where the key is the surface id and the value is a Surface object for easy reference.
        :param cells: Optional dict of cells where the key is the cell id and the value is a Cell object for easy reference.
        :param materials: Optional dict of materials where the key is the material name and the value is a Material object for easy reference.
        :param tallies: Optional dict of tallies where the key is the tally id and the value is a Tally object for easy reference.
        :param physics: Optional dict of physics settings where the key is the setting name and the value is the setting value.
        """
        # add dict self.surfaces = surfaces if surfaces is not None else {}
       

        self.surfaces = surfaces
        self.cells = cells
        self.materials = materials
        self.tallies = tallies
        self.transformations = transformations
        self.physics = physics
        self.block_locations = block_locations

        # add default material
        self.materials[0] = "Void"

    def add_surfaces(self, surfaces):
        """Adds surfaces to the model from surface list."""
        if surfaces is not None and type(surfaces) == list:
            for surface in surfaces:
                self.add_surface(surface)
        elif surfaces is not None and type(surfaces) == dict:
            for key in surfaces:
                self.add_surface(surfaces[key])

    def add_surface(self, surface):
        """Adds surfaces to the model."""
        if surface is not None:
            self.surfaces[surface.surface_id] = surface

    def add_cells(self, cells):
        """Adds cells to the model from cell list."""
        if cells is not None and type(cells) == list:
            for cell in cells:
                self.add_cell(cell)

    def add_cell(self, cell):
        """Adds cells to the model."""
        if cell is not None:
            self.cells[cell.cell_id] = cell

    def add_materials(self, materials):
        """Adds materials to the model from material list."""
        if materials is not None and type(materials) == list:
            for material in materials:
                self.add_material(material)

    def add_material(self, material):
        """Adds materials to the model."""
        if material is not None:
            self.material[material.id] = material

    def add_tally(self, tally):
        """ add tally instance to the model tally dictionary"""
        if tally is not None:
            self.tallies[tally.id] = tally

    def add_tallies(self, tallies):
        """ add tallies to the model tallies dictionary"""
        if tallies is not None and type(tallies) == list:
            for tally in tallies:
                self.add_tally(tally)

    def add_physics(self, physics):
        """Adds physics settings to the model."""
        if physics is not None:
            self.physics = physics

    def get_item_by_name(self, item_type, item_name):
        """
        This function returns the item with the given name and type.
        """
        
        if item_type == "surface":
            return self.surfaces.get(item_name)
        elif item_type == "cell":
            return self.cells.get(item_name)
        elif item_type == "material":
            return self.materials.get(item_name)
        elif item_type == "tally":
            return self.tallies.get(item_name)
        else:
            return None

    @classmethod
    def from_file_parser(cls, file_parser):
        """
        Class method to initialize the ModelMcnpInput instance from a file parser object.

        :param file_parser: An object capable of parsing MCNP input files and extracting components.
        :return: An instance of ModelMcnpInput initialized with the components extracted by the file_parser.
        """
        surfaces = file_parser.get_surfaces()
        cells = file_parser.get_cells()
        materials = file_parser.get_materials()
        tallies = file_parser.get_tallies()
        physics = file_parser.get_physics()
        block_locations = file_parser.block_locations
        transformations = file_parser.get_transformations()

        return cls(surfaces, cells, materials, tallies, physics, block_locations, transformations)

    def get_surface(self, surface_id):
        """
        This function returns the surface with the given number.
        """
        return self.surfaces.get(surface_id, "Surface {}: The Machine god doesn't recognize this surface".format(surface_id))
        
    def get_cell(self, cell_id):
        """
        This function returns the cell with the given number.
        """
        return self.cells.get(cell_id, "Cell {}: The Machine god doesn't recognize this cell".format(cell_id))

    def get_material(self, material_id):
        """ 
        This function returns the material with the given number.
        """
        return self.materials.get(material_id, "Material {}: The Machine god doesn't recognize this material".format(material_id))

    def get_tally(self, tally_id):
        """
        This function returns the tally with the given number.
        """
        return self.tallies.get(tally_id, "Tally {}: The Machine god doesn't recognize this tally".format(tally_id))

    def get_transformation(self, transformation_id):
        """
        This function returns the transformation with the given number.
        """
        return self.transformations.get(transformation_id, "Transformation {}: The Machine god doesn't recognize this transformation".format(transformation_id))

    def return_block_type(self, line_number):
        """
        This function returns the type of block the line is in.

        Args:
            line_number (int): The line number to check.

        Returns:
            str: The type of block ('surface', 'cell', 'physics') or None if not in any block.
        """
        for block_type in ['surfaces', 'cells', 'physics']: 
            if self.block_locations[block_type]['start'] <= line_number <= self.block_locations[block_type]['end']:
                
                return block_type
        return None

class HandlerMcnpInput(object):
    """
    The intention of this class is to modify the ModelMcnpInput object by changing the surfaces and materials in the cells as needed.
    """
    def __init__(self, model_mcnp_input):
        self.model = model_mcnp_input

    def replace_surface_in_cell_block(self, old_surface_id, new_surface):

        """
        iterate over the cell dictionarry and replace the old surface with the new surface
        """
        for cell_id in self.model.cells:
            cell = self.model.cells[cell_id]
            cell.replace_surface(old_surface_id, new_surface)

    def replace_material_in_cell_block(self, old_material_name, new_material):
        for cell in self.model.cells:
            if cell.material.name == old_material_name:
                cell.material = new_material

    def replace_surface_parameters_in_surface_block(self, old_surface_id, new_surface):
        # get the old_surface_id from model surfaces dict and replace the parameters with new_surface parameters
        # use dict get method to get the surface with old_surface_id
        self.model.surfaces.get(old_surface_id).update_surface_parameters(new_surface.parameters)


    def replace_surface_in_surface_block(self, old_surface_id, new_surface):
        """
        This replaces the surface definition in surface block changing the surface id and parameters.
        """
        self.model.surfaces.get(old_surface_id).update_surface(new_surface.surface_id, new_surface.parameters)
            

    def replace_surface(self, old_surface_id, new_surface):
        """
        This function replaces the old surface with the new surface in the model (cell block and surface block).
        """
        self.replace_surface_in_cell_block(old_surface_id, new_surface)
        self.replace_surface_in_surface_block(old_surface_id, new_surface)
    # Placeholder for additional methods
"""
if  __name__ == "__main__":
        
    # Example for model creation and modification
    model = ModelMcnpInput()
    model.add_surface(Surface(1, "box", parameters="1 2 3 4 5 6", comment="surface 1"))
    model.add_surface(Surface(2, "box", parameters="7 8 9", comment="surface 2"))
    model.add_cell(Cell(cell_id=1, material_id=1, surfaces=[1,2],cells= [],importance= 1))   
    # Print surfaces before modification
    print("Before modification:")
    for surface in model.surfaces:
        print(surface)

    # Use Handler to modify a surface
    handler = HandlerMcnpInput(model)
    handler.replace_surface(2, Surface(1, "px", parameters="4", comment="surface 3"))

    # Print surfaces after modification
    print("\nAfter modification:")
    for key in model.surfaces:
        print(model.surfaces[key])
    """