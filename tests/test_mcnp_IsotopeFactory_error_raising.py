from __future__ import division, print_function
import pytest
from npp_mcnp_plugin.models.mcnp_input_cards import IsotopeFactory

# Test data for invalid input cases
invalid_test_data = [
    ("1001a.70c",0.0,  ValueError,  "Invalid value '1001a' provided. Expected an integer."),
    ("1001.70c", "a1",  ValueError, "Abundance (a1) is not a valid number"),
]

@pytest.mark.parametrize("input_value, abundance, expected_exception, expected_message", invalid_test_data)
def test_isotope_factory_errors(input_value, abundance, expected_exception, expected_message):
    """
    Test the IsotopeFactory's error handling.
    """
    factory = IsotopeFactory()

    with pytest.raises(expected_exception) as exc_info:
        print(exc_info)
        factory.create_isotope_from_input(input_value, abundance)

    assert expected_message in str(exc_info.value), \
        "Expected message not found in exception for input '{}'".format(input_value)

if __name__ == "__main__":
    pytest.main()