import pytest
from npp_mcnp_plugin.models.mcnp_input_cards import CellFactory

# Test data for invalid input cases
invalid_test_data = [
    ("999 a 0 -404:405:408           imp:n=0", "Input line format is invalid"), 
    ("999a  0 -404:405:408           imp:n=0", "Input line format is invalid"),
]

@pytest.mark.parametrize("invalid_line, expected_message", invalid_test_data)
def test_cell_creation_invalid_input(invalid_line, expected_message):
    # Check if ValueError is raised with the correct message
    with pytest.raises(ValueError) as exc_info:
        CellFactory.create_from_input_line(invalid_line)
    
    # Assert that the exception message matches the expected message
    assert str(exc_info.value) == expected_message, \
        "Failed for '{}': actual message={} != expected message={}".format(
            invalid_line, str(exc_info.value), expected_message
        )
