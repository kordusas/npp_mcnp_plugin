import pytest
from npp_mcnp_plugin.models.mcnp_input_cards import CellFactory

# Test data for invalid input cases
invalid_test_data = [
    ("999 a 0 -404:405:408           imp:n=0", "Input line format is invalid"), 
    ("999a  0 -404:405:408           imp:n=0", "Input line format is invalid"),
    ("999  r0 -404:405:408           imp:n=0", "Input line format is invalid"),
    ("999  0 -404 405 408w           imp:n=0", "Cell entry is not a valid integer: 408w"),
    ("x  r0 -404:405:408           imp:n=0", "Input line format is invalid"),
    ("99  0 -404:405:408         vol= x  imp:n=0", "could not convert string to float: x"),
     ("10  0 -404:405:408         u= x  imp:n=0", "Invalid value 'x' provided. Expected an integer.")
]

@pytest.mark.parametrize("invalid_line, expected_message", invalid_test_data)
def test_cell_creation_invalid_input(invalid_line, expected_message):
    # Check if ValueError is raised with the correct message
    with pytest.raises(ValueError) as exc_info:
        CellFactory.create_from_input_line(invalid_line)
    
    print("ValueError: ", exc_info.value)
    # Assert that the exception message matches the expected message
    assert str(exc_info.value) == expected_message, \
        "Failed for '{}': actual message={} != expected message={}".format(
            invalid_line, str(exc_info.value), expected_message
        )
