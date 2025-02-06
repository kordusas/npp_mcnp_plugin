import pytest
try:
    from npp_mcnp_plugin.models.mcnp_cell_factory import CellFactory
except ImportError as e:
    from models.mcnp_cell_factory import CellFactory
    print(e)

# Define test cases as tuples of input lines and expected attributes
test_data = [
    ("999 0 -404:405:408           imp:n=0", 
     {"id": 999, "material_id": 0, "density": 0, "surfaces": [404, 405, 408], "importance": {"n": 0}, "data_cards": {}}),

    ("3 0 (-3 1 2):(-2 -1)", 
     {"id": 3, "material_id": 0, "density": 0, "surfaces": [3, 1, 2, 2, 1], "importance": {"n": None}, "data_cards": {}}),

    ("12  81 -2.35 1 -3   -13 12 imp:n=1", 
     {"id": 12, "material_id": 81, "density": -2.35, "surfaces": [1, 3, 13, 12], "importance": {"n": 1}, "data_cards": {}}),

    ("11 0 1 -2 imp:n=1", 
     {"id": 11, "material_id": 0, "density": 0, "surfaces": [1, 2], "importance": {"n": 1}, "data_cards": {}}),

    ("11 0 1 -2 3 -4", 
     {"id": 11, "material_id": 0, "density": 0, "surfaces": [1, 2, 3, 4], "importance": {}, "data_cards": {}}),

    ("14  81 -2.35 1 -3   -15 14 imp:n =1", 
     {"id": 14, "material_id": 81, "density": -2.35, "surfaces": [1, 3, 15, 14], "importance": {"n": 1}, "data_cards": {}}),

    ("23 12   -9.024 (3 -4 101 -102) #2        imp:n=1 u=   4 vol =106.478", 
     {"id": 23, "material_id": 12, "density": -9.024, "surfaces": [3, 4, 101, 102], 
      "importance": {"n": 1}, "data_cards": {"u": 4, "vol": 106.478}}),
      
    ("24 12   -9.024 (1: -2: 3:-4) #2        imp:n=1 u=4 vol =106.478", 
     {"id": 24, "material_id": 12, "density": -9.024, "surfaces": [1, 2, 3, 4], 
      "importance": {"n": 1}, "data_cards": {"u": 4, "vol": 106.478}})
]

@pytest.mark.parametrize("line, expected_attributes", test_data)
def test_cell_creation(line, expected_attributes):
    # Create the cell using the factory
    cell = CellFactory.create_from_input_line(line)
    
    # Assert each attribute matches expected values
    for attr_name, expected_value in expected_attributes.items():
        actual_value = getattr(cell, attr_name)
        if isinstance(expected_value, dict):
            for key, value in expected_value.items():
                assert actual_value.get(key) == value, \
                    "Failed for {}: key={} actual={} != expected={}".format(attr_name, key, actual_value.get(key), value)
        else:
            assert actual_value == expected_value, \
                "Failed for {}: actual={} != expected={}".format(attr_name, actual_value, expected_value)
    
    # Print success message
    print("Test passed for cell: '{}'".format(cell.id))
