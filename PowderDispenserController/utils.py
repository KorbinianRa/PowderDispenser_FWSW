"""
Utility functions for managing and configuring the powder dispensing system.

This module provides functionality to:
- Interact with hardware (e.g., listing and selecting serial ports).
- Manage system configurations (load, save, and modify settings).
- Log dispensing operations and analyze data using log files.

Functions:
    list_serial_ports() - Lists all available serial ports and their details.
    get_serial_port() - Automatically retrieves a serial port associated with a USB serial device.
    get_config(config_file) - Loads the configuration settings from a JSON file.
    save_config(config_file, powder_config) - Saves configuration settings to a JSON file.
    read_logfile(logfile) - Reads dispensing operation logs into a pandas DataFrame.
    write_to_logfile(logfile, **kwargs) - Appends dispensing operation details into a logfile.
"""

import json
import serial
import serial.tools.list_ports
import pandas as pd
import ast

def list_serial_ports():
    """
    Lists all available serial ports on the system along with their details.

    This function prints the following information for each detected serial port:
    - Port (e.g., COM3 or /dev/ttyUSB0)
    - Description (e.g., Arduino device name)
    - Hardware ID (e.g., USB vendor and product IDs)

    Useful for debugging hardware connections.
    """
    ports = serial.tools.list_ports.comports()  # Get all available serial ports.
    for port in ports:
        print(f"Port: {port.device}, Description: {port.description}, Hardware ID: {port.hwid}")  # Print port details.

def get_serial_port():
    """
    Automatically retrieves the serial port associated with a USB serial device.

    Returns:
        str: The name of the first detected serial port with a description containing 'serial'.

    Raises:
        Exception: If no USB serial port is detected.
    """
    ports = serial.tools.list_ports.comports()  # Get all available serial ports.
    for port in ports:
        if 'serial' in port.description.lower():  # Look for ports with 'serial' in their description.
            return port.device  # Return the port name (e.g., COM3 or /dev/ttyUSB0).
    raise Exception(
        "ERROR: No USB Serial Port Found. Please try again or define the port manually using list_serial_ports()."
    )

def get_config(config_file):
    """
    Loads configuration settings from a JSON file.

    Parameters:
        config_file (str): The path to the configuration file.

    Returns:
        dict: The loaded configuration settings.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
    """
    try:
        with open(config_file, "r") as file:  # Open the configuration file in read mode.
            powder_config = json.load(file)  # Parse the JSON content into a dictionary.
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Error: '{config_file}' file not found. Please make sure the file exists in the current directory."
        )
    return powder_config  # Return the loaded configuration dictionary.

def save_config(config_file, powder_config):
    """
    Saves configuration settings to a JSON file.

    Parameters:
        config_file (str): The path to the configuration file.
        powder_config (dict): The configuration settings to be saved.

    This function overwrites the file with the new configuration settings.
    """
    with open(config_file, 'w') as f:  # Open the configuration file in write mode.
        json.dump(powder_config, f, indent=4)  # Save the configuration as a formatted JSON file.
    print(f"Configuration saved to {config_file}")  # Confirm that the configuration has been saved.

def read_logfile(logfile):
    """
    Reads a dispensing operation log file into a pandas DataFrame.

    Parameters:
        logfile (str): The path to the logfile.

    Returns:
        pandas.DataFrame: The loaded log data with parsed lists in specific columns.

    Behavior:
        - Parses string representations of lists in specific columns (e.g., 'desired_amount', 'measured_amount').
        - If the log file does not exist, raises a FileNotFoundError.
    """
    df = pd.read_csv(logfile)  # Load the CSV file into a DataFrame.
    
    # Columns that may contain string representations of lists (to be converted to actual lists).
    list_columns = ['desired_amount', 'measured_amount', '# of steps']

    for column in df.columns:
        if column in list_columns and df[column].dtype == object:
            # Convert string representations of lists into actual Python lists.
            df[column] = df[column].apply(ast.literal_eval)
    return df  # Return the parsed DataFrame.

def write_to_logfile(logfile, desired_amount=None, measured_amount=None, steps=None, augerType=None, powderType=None, filterType=None):
    """
    Appends dispensing operation details into a logfile.

    Parameters:
        logfile (str): The path to the logfile.
        desired_amount (float, optional): The target amount to be dispensed.
        measured_amount (float, optional): The actual amount dispensed as measured by the scale.
        steps (int, optional): The number of steps executed by the stepper motor.
        augerType (str, optional): The type of auger used for dispensing.
        powderType (str, optional): The type of powder dispensed.
        filterType (str, optional): The type of filter applied to the weight measurement.

    Behavior:
        - Reads the existing log file into a DataFrame.
        - Appends the new row of data to the DataFrame.
        - Saves the updated DataFrame back to the log file.
    """
    # Create a new row with the provided data.
    new_row = {
        'desired_amount': [desired_amount] if desired_amount is not None else None,
        'measured_amount': [measured_amount] if measured_amount is not None else None,
        '# of steps': [steps] if steps is not None else None,
        'auger_type': [augerType] if augerType is not None else None,
        'powder_type': [powderType] if powderType is not None else None,
        'filter_type': [filterType] if filterType is not None else None
    }

    try:
        log_df = read_logfile(logfile)  # Load the existing log file into a DataFrame.
    except FileNotFoundError:
        # If the log file does not exist, create an empty DataFrame with appropriate columns.
        log_df = pd.DataFrame(columns=new_row.keys())

    # Append the new row to the DataFrame.
    append_df = pd.DataFrame(new_row)
    if log_df.empty:
        log_df = append_df
    else:
        log_df = pd.concat([log_df, append_df], ignore_index=True).reset_index(drop=True)

    # Save the updated DataFrame back to the log file.
    log_df.to_csv(logfile, index=False)
