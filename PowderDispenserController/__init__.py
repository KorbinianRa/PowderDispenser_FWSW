"""
Initialization module for the powder dispensing package.

This module sets up the namespace and imports for the components of the powder dispensing system,
ensuring that all necessary components are available for use when the package is imported.

Imports:
    - PowderDispenseController: The main controller class responsible for managing powder dispensing operations.
    - Utility functions for serial port detection, configuration management, and log handling.

Attributes:
    __all__: A list of public objects exposed by this module. These objects represent the components
             of the package that are accessible when using `from package import *`.
"""

# Import the main controller class for powder dispensing.
from .controller import PowderDispenseController

# Import utility functions for managing serial ports and configurations.
from .utils import list_serial_ports, get_serial_port

# Define the list of public objects exposed by this module.
__all__ = [
    'PowderDispenseController',  # Main powder dispensing controller.
    'list_serial_ports',         # Function to list available serial ports.
    'get_serial_port',           # Function to retrieve a serial port.
    'read_logfile',              # Utility function to read log files (if defined elsewhere).
    'write_to_logfile',          # Utility function to write to log files (if defined elsewhere).
    'get_config',                # Function to retrieve the system's configuration.
    'save_config'                # Function to save the updated configuration.
]
