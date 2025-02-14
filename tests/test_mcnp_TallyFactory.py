from __future__ import division, print_function
import pytest
from npp_mcnp_plugin.models.mcnp_input_cards import Tally

# Define test cases as tuples of input lines and expected attributes
test_data = [
    ("f14:n 10 12", {}),

]

@pytest.mark.parametrize("line, expected_attributes", test_data)
def test_surface_creation(line, expected_attributes):
    # Create the surface using the factory method
    surface = Tally.create_from_input_line(line, expected_attributes.get("comment"))
    
    # Assert each attribute matches expected values
    for attr_name, expected_value in expected_attributes.items():
        actual_value = getattr(surface, attr_name)
        assert actual_value == expected_value, \
            "Failed for {}: actual={} != expected={}".format(attr_name, actual_value, expected_value)
    
    # Print success message
    print("Test passed for surface: '{}'".format(surface.id))

if __name__ == "__main__":
    pytest.main()
