import sys
import os
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.mcnp_input_cards import CellFactory, Cell

def main(line,verbose=False):
    if  verbose: print("Testing line: \n" + str(line))
    cell, error = CellFactory.create_from_input_line(line)
    if verbose: print(cell)
    return cell

def assert_cell_attributes(cell, expected_attributes):
    """Asserts that the cell's attributes match the expected values."""
    for attr_name, expected_value in expected_attributes.items():
        
        if attr_name == "importance":
            continue
        actual_value = getattr(cell, attr_name)
        assert actual_value == expected_value, \
            "Assertion failed for {}: expected {}, got {}".format(attr_name, expected_value, actual_value)
    
    print("All assertions passed for cell {} ".format(cell.id))


if __name__ == "__main__":
    test_cell_lines_list = [ 
        "999 0 -404:405:408           imp:n=0",
        "3 0 (-3 1 2):(-2 -1)",
        "12  81 -2.35 1 -3   -13 12 imp:n=1",
        "11 0 1 -2 imp:n=1",
        "11 0 1 -2 3 -4",
        "14  81 -2.35 1 -3   -15 14 imp:n =1",
        "23 12   -9.024 (3 -4 101 -102) #2        imp:n=1 u=   4 vol =106.478",
        "24 12   -9.024 (1: -2: 3:-4) #2        imp:n=1 u=4 vol =106.478"
    ]

    expected_attributes_list = [
        {"id": 999, "material_id": 0, "density": 0,  "surfaces": [404, 405, 408], "importance": {"n": 0}},
        {"id": 3, "material_id": 0, "density": 0,  "surfaces": [3,1,2,2,1], "importance": {"n": 0}},
        {"id": 12, "material_id": 81, "density": -2.35,"surfaces": [1, 3, 13, 12], "importance": {"n": 1}},
        {"id": 11, "material_id": 0, "density": 0,"surfaces": [1, 2], "importance": {"n": 1}},
        {"id": 11, "material_id": 0, "density": 0,"surfaces": [1, 2, 3, 4], "importance": {}},
        {"id": 14, "material_id": 81, "density": -2.35,"surfaces": [ 1, 3, 15, 14], "importance": {"n": 1}},
        {"id": 23, "material_id": 12, "density": -9.024,"surfaces": [3, 4, 101, 102], "importance": {"n": 1}, "universe": 4, "volume": 106.478},
        {"id": 24, "material_id": 12, "density": -9.024,"surfaces": [1,2,3,4], "importance": {"n": 1}, "universe": 4, "volume": 106.478}
    ]

    for line, expected_attributes in zip(test_cell_lines_list, expected_attributes_list):
        test_cell = main(line, verbose=False)
        
        assert_cell_attributes(test_cell, expected_attributes)