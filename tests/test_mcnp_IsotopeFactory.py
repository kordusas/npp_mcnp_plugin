from __future__ import division, print_function
import pytest
from npp_mcnp_plugin.models.mcnp_input_cards import IsotopeFactory

# Consolidated test data: (input_value, method, expected_zaid, expected_name, expected_z, expected_a, expected_abundance, expected_library)
test_data = [
    (1001, "create_isotope", 1001, "H", 1, 1, 0.99985, "70c"),
    (2004, "create_isotope", 2004, "He", 2, 4, 0.999863, "70c"),
    (8016, "create_isotope", 8016, "O", 8, 16, 0.99757, "70c"),
    (92235, "create_isotope", 92235, "U", 92, 235, 0.007204, "70c"),
    ("1001.70c", "create_isotope_from_input", 1001, "H", 1, 1, 0.99985, "70c"),
    ("2004.70c", "create_isotope_from_input", 2004, "He", 2, 4, 0.999863, "70c"),
    ("92235.60c", "create_isotope_from_input", 92235, "U", 92, 235, 0.007204, "60c"),
]

@pytest.mark.parametrize(
    "input_value, method, expected_zaid, expected_name, expected_z, expected_a, expected_abundance, expected_library",
    test_data
)
def test_isotope_factory(input_value, method, expected_zaid, expected_name, expected_z, expected_a, expected_abundance, expected_library):
    """
    Test the IsotopeFactory's creation methods.
    """
    factory = IsotopeFactory()

    # Call the appropriate factory method
    if method == "create_isotope":
        isotope = factory.create_isotope(input_value, expected_abundance, expected_library)
    elif method == "create_isotope_from_input":
        isotope = factory.create_isotope_from_input(input_value, expected_abundance)
    else:
        raise ValueError("Unknown method: {}".format(method))

    # Validate the properties of the created isotope
    assert isotope.zzzaaa == expected_zaid, "zzzaaa mismatch: {} != {}".format(isotope.zzzaaa, expected_zaid)
    assert isotope.name == expected_name, "Name mismatch: {} != {}".format(isotope.name, expected_name)
    assert isotope.z == expected_z, "Z mismatch: {} != {}".format(isotope.z, expected_z)
    assert isotope.a == expected_a, "A mismatch: {} != {}".format(isotope.a, expected_a)
    assert isotope.abundance == expected_abundance, "Abundance mismatch: {} != {}".format(isotope.abundance, expected_abundance)
    assert isotope.library == expected_library, "Library mismatch: {} != {}".format(isotope.library, expected_library)

if __name__ == "__main__":
    pytest.main()
