
## Structure and Interaction

The architecture of the plugin is designed around a core concept: the MCNP input parser class. This class is responsible for parsing the content of an MCNP input file into a structured `mcnp_input` class. This structured format allows for efficient interaction with the file's content, enabling users to query and retrieve information about the input directly from an instance of the `mcnp_input` class.

To ensure the plugin remains responsive and up-to-date with the latest changes made by the user, the input file is re-parsed every time it is saved. This approach guarantees that the information provided by the plugin is always accurate, though we are considering optimizations to improve parsing speed for larger files.

The `on_selection` function is where the magic happens. It:

1. Creates an instance of the `text` class based on that selection.
2. Determines the block within the MCNP input file where the selection is located.
3. Identifies the specific content that is selected.
4. Matches this identified information against the structured data within the `mcnp_input` class instance to provide contextual information back to the user.

For the autocomplete feature, a similar approach will be implemented. The autocomplete functionality will leverage the structured `mcnp_input` class to suggest relevant MCNP keywords and parameters as the user types. This will not only enhance the user experience by providing real-time suggestions but also help in minimizing syntax errors by suggesting only valid options based on the current context within the file. The autocomplete system will be context-aware, adjusting its suggestions based on the specific block the user is editing (e.g., within a cell block, surface block, or material block), ensuring that the suggestions are always relevant and helpful.

The MCNP error popup is handled by error collection

The error class instances are created in two locations:

- file_parser class if instance creation failed this produces error and if possible returns incomplete instance and error message
- in main handler class after mcnp_input is already created and separate parts are validated by the validator class