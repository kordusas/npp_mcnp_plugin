# NPP_MCNP_Plugin

## Introduction
NPP_MCNP_Plugin is an extension for Notepad++ designed to enhance the productivity of users working with MCNP (Monte Carlo N-Particle) files. It offers model analytics, including surface, cell, and material tracking, directly within the Notepad++ environment.


## Features

### Generative Methods
- **Status**: Planned 
- **Description**: impement generative methods to simplify MCNP input writting. 
  - implement command to auto generate basic input structure, for example \generate input creates all basic blocks of MCNP input 
  - implement LLM based input generation for example \generate input with beam neutron source and a collimator for detector simulations
  -  

### Autocomplete 
- **Status**: Planned
- **Status**: Planned
- **Description**: A future enhancement to introduce an autocomplete feature that suggests MCNP keywords and parameters as you type. This aims to boost productivity by offering real-time suggestions and minimizing syntax errors. The feature will be context-aware, providing suggestions based on the specific block you are working in:
  - **In Cell Block**:
    - Suggest autocomplete surface ID during typing from the available surface dictionary. 
    - suggest autocoplete the cell name after #. 
    - Suggest a new cell ID after a newline in the cell block. 
    - Suggest a material ID; a popup should provide basic info about the material, such as the comment line of the material or top isotopes in abundance.
    - Suggest available transformations after typing "trcl". 
  - **In Surface Block**:
    - Suggest a new surface ID after a newline.
    - Auto-popup to show available transformations when typed "\tr".
  - **In Physics Block**:
    - When in tallies, suggest available surfaces or cells depending on the tally. This will require context awareness about what type of tally it is.


### Cells Block Information
- **Status**: Partially Implemented
- **Description**: For cell blocks, 
- selecting a specific cell displays a list of other cells where that cell is used, facilitating a deeper understanding of cell interactions within the model. (need cell parsing)
- Selecting the material popups info about the material. (completed)
- selecting surfaces popups information about the selected surfaces. (completed)

### Surfaces Block Information
- **Status**: Completed
- **Description**: 
  - selecting a surface type provides information about that type. May add more surface types in data/surface_info.json 
  - selecting the transformation popups info about that trcl

### Physics Block Information
- **Status**: Planned
- **Description**: Plans to develop functionalities for physics blocks are in place. This will allow users to access pertinent information and insights specific to physics blocks.
   - pop information about surfaces in ssr/ssw card
   - info about cells in ssr/ssw card
   - info about cells in sdef
   - info about surfaces in sdef

### MCNP Error Checking 
- **Status**: Partially Implemented
- **Description**: Pops a message after parsing the MCNP input and checking if 
   -  tally particle identifiers are valid
   -  +f6 tally doesnt have a particle identifier
   -  tally parameters (cells or surfaces) are missing
   -  tally is missing
   -  surface type is valid
   -  transformation parameters are missing


## Installation
1. Download the latest release of Python Script
2. Navigate to the Notepad++ installation path 
3. place the npp_mcnp_plugin directory in the ../plugins/PythonScript/lib folder
4. place the main.py file in the ../plugins/PythonScript/scripts


## Usage

After installation, the plugin can be accessed via the `plugins -> PythonScript -> scripts ` menu in Notepad++. 

One can set up the shortcuts to the script following the advise in the discussion: https://community.notepad-plus-plus.org/topic/14703/run-python-script-pythonscript-plugin-with-a-shortcut/3

## Examples 

Notification on cell block and surface block information happens once you select the card of interest. 

![](selection_notification_example.gif)

The error checking happens every time you save a file and pops a separate window with comprehensive information. 


![](error_message_popup_example.gif)


## Structure and Interaction

The architecture of the plugin is designed around a core concept: the MCNP input parser class. This class is responsible for parsing the content of an MCNP input file into a structured `mcnp_input` class. This structured format allows for efficient interaction with the file's content, enabling users to query and retrieve information about the input directly from an instance of the `mcnp_input` class.

To ensure the plugin remains responsive and up-to-date with the latest changes made by the user, the input file is re-parsed every time it is saved. This approach guarantees that the information provided by the plugin is always accurate, though we are considering optimizations to improve parsing speed for larger files.

The `on_selection` function is where the magic happens. It:
1. Creates an instance of the `text` class based on that selection.
2. Determines the block within the MCNP input file where the selection is located.
3. Identifies the specific content that is selected.
4. Matches this identified information against the structured data within the `mcnp_input` class instance to provide contextual information back to the user.

For the autocomplete feature, a similar approach will be implemented. The autocomplete functionality will leverage the structured `mcnp_input` class to suggest relevant MCNP keywords and parameters as the user types. This will not only enhance the user experience by providing real-time suggestions but also help in minimizing syntax errors by suggesting only valid options based on the current context within the file. The autocomplete system will be context-aware, adjusting its suggestions based on the specific block the user is editing (e.g., within a cell block, surface block, or material block), ensuring that the suggestions are always relevant and helpful.


The MCNP error popu is handled by errorcollection

The error class instances are created in two locations:
-  file_parser class if instance creation failed this produces error. 
-  in main handler class after mcnp_input is already created and separate parts are validated by the validator class