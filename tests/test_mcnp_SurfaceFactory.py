from __future__ import division, print_function
import pytest
from npp_mcnp_plugin.models.mcnp_input_cards import Surface

# Define test cases as tuples of input lines and expected attributes
test_data = [
    ("1 px 0.0", {"id": 1, "surface_type": "px", "parameters": "0.0", "transformation": None, "comment": None}),
    ("2 py 1.0", {"id": 2, "surface_type": "py", "parameters": "1.0", "transformation": None, "comment": None}),
    ("3 pz -1.0", {"id": 3, "surface_type": "pz", "parameters": "-1.0", "transformation": None, "comment": None}),
    ("4 5 px 2.0", {"id": 4, "surface_type": "px", "parameters": "2.0", "transformation": "5", "comment": None}),
]

@pytest.mark.parametrize("line, expected_attributes", test_data)
def test_surface_creation(line, expected_attributes):
    # Create the surface using the factory method
    surface = Surface.create_from_input_line(line, expected_attributes.get("comment"))
    
    # Assert each attribute matches expected values
    for attr_name, expected_value in expected_attributes.items():
        actual_value = getattr(surface, attr_name)
        assert actual_value == expected_value, \
            "Failed for {}: actual={} != expected={}".format(attr_name, actual_value, expected_value)
    
    # Print success message
    print("Test passed for surface: '{}'".format(surface.id))

if __name__ == "__main__":
    pytest.main()
