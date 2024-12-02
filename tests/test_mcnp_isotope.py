import pytest
from npp_mcnp_plugin.models.mcnp_input_cards import Isotope

# Test data for from_zzzaaa method: (zzzaaa, expected_zaid, expected_name, expected_z, expected_a, expected_abundance, expected_library, expected_name)
from_zzzaaa_test_data = [
    (1001, 1001, "H", 1, 1, 0.99985, ".70c", ),
    (2004, 2004, "He", 2, 4, 0.999863, ".70c", ),
    (8016, 8016, "O", 8, 16, 0.99757, ".70c", ),
    (92235, 92235, "U", 92, 235, 0.007204, ".70c", ),
]

@pytest.mark.parametrize("zzzaaa, expected_zaid, expected_name, expected_z, expected_a, expected_abundance, expected_library", from_zzzaaa_test_data)
def test_isotope_from_zzzaaa(zzzaaa, expected_zaid, expected_name, expected_z, expected_a, expected_abundance, expected_library):
    isotope = Isotope.from_zzzaaa(zzzaaa, expected_abundance,expected_library)
    
    assert isotope.zzzaaa == expected_zaid
    assert isotope.name == expected_name
    assert isotope.z == expected_z
    assert isotope.a == expected_a
    assert isotope.abundance == expected_abundance
    assert isotope.library == expected_library
    assert isotope.name == expected_name

if __name__ == '__main__':
    pytest.main()