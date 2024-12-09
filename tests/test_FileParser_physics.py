import pytest, os
from npp_mcnp_plugin.utils.file_parser  import FileParser
from npp_mcnp_plugin.models.error  import ErrorCollection


def write_block_to_files(block, key):
    """
    This function writes the content of a given block to a file based on a provided key.

    Parameters:
    block (dict): A dictionary containing blocks of data. The function expects a block with the given key.
    key (str): The key to access the specific block within the dictionary.

    Returns:
    None. The function writes the content to a file and prints a confirmation message.
    """
    # Get the current working directory
    current_dir = os.getcwd()

    # Construct the file path
    filename = os.path.join(current_dir, "tests", "{}.txt".format(key))

    # Merge the list into a single string with newline characters
    content = '\n'.join(str(item) for item in block)

    # Open the file for writing and write the merged content
    with open(filename, 'w') as f:
        f.write(content)

    # Print confirmation message
    print ("Written content for key '{}' to {}".format(key, filename))

             
# Test function
def test_parse_physics_block():
    """
    Test whether the physics block parsed by FileParser matches the expected output.
    """
    # Path to the input file in the mcnp_example_inputs directory
    input_file = "mcnp_example_inputs/input_1.i"

    # Define the expected physics block content
    correct_physics_block = [
        "c graphite density -2.2",
        "c ------------------------------------------------------------------------------",
        "c aluminum   al",
        "m60         6000  1",
        "c concrete density -2.35   hydrogen",
        "m13           13027 1.000000000",
        "c carbon  oxygen sodium  magnesium aluminum silicon potassiu calcium iron       type",
        "m81 1001    -0.01    6000    -0.001    8016    -0.52    11023   -0.02    12024   -0.002    13027   -0.034    14028   -0.34    19039   -0.013    20040   -0.044    26056   -0.014",
        "c source",
        "mode        n",
        "sdef pos 0 0 0 erg  14 par n vec 0 0 1",
        "f4:n 1"
    ]

    # Instantiate the FileParser with the mock error collection
    error_collection = ErrorCollection()
    parser = FileParser.from_file(input_file, error_collection)
    
    # Get the actual physics block
    actual_physics_block = parser.block["physics"]
    write_block_to_files(actual_physics_block, "physics")
    print(actual_physics_block)
     # Assert line by line
    assert len(actual_physics_block) == len(correct_physics_block), \
        "Number of lines in physics block does not match. Expected {}, got {}".format(len(correct_physics_block),len(actual_physics_block) )

    for i, (expected_line, actual_line) in enumerate(zip(correct_physics_block, actual_physics_block), start=1):
        assert expected_line == actual_line, \
            "Mismatch at line {}: expected '{}', got '{}'".format(i,expected_line, actual_line)



