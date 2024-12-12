"""
Utility functions for managing and configuring the powder dispensing system.
Provides functionality to interact with hardware, manage configurations, and log operations.

Functions:
    list_serial_ports() - Lists all available serial ports.
    get_serial_port(port_name) - Retrieves a specific serial port.
    get_config(config_file) - Loads the configuration from a file.
    save_config(config_file, powder_config) - Saves the configuration to a file.
    read_logfile(logfile) - Reads a logfile into a pandas DataFrame.
    write_to_logfile(logfile, **kwargs) - Writes dispensing details into a logfile.
"""

import json
import serial
import serial.tools.list_ports
import pandas as pd
import ast

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Port: {port.device}, Description: {port.description}, Hardware ID: {port.hwid}")

def get_serial_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if 'serial' in port.description.lower():
            return port.device
    raise Exception("ERROR: No USB Serial Port Found. Please try again or define port manually using list_serial_ports().")

def get_config(config_file):
    try:
        with open(config_file, "r") as file:
            powder_config = json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"Error: '{config_file}' file not found. Please make sure the file exists in the current directory.")
    return powder_config

def save_config(config_file, powder_config):
    with open(config_file, 'w') as f:
        json.dump(powder_config, f, indent=4)
    print(f"Configuration saved to {config_file}")

def read_logfile(logfile):
    df = pd.read_csv(logfile)
    # List of columns that might contain string representations of lists
    list_columns = ['desired_amount', 'measured_amount', '# of steps']

    for column in df.columns:
        if column in list_columns and df[column].dtype == object:
            df[column] = df[column].apply(ast.literal_eval)
    return df

def write_to_logfile(logfile, desired_amount = None, measured_amount = None, steps = None, augerType = None, powderType = None, filterType = None):
    new_row = {
        'desired_amount': [desired_amount] if desired_amount is not None else None,
        'measured_amount': [measured_amount] if measured_amount is not None else None,
        '# of steps': [steps] if steps is not None else None,
        'auger_type': [augerType] if augerType is not None else None,
        'powder_type': [powderType] if powderType is not None else None,
        'filter_type': [filterType] if filterType is not None else None
    }
    
    try:
        log_df = read_logfile(logfile)
    except FileNotFoundError:
        log_df = pd.DataFrame(columns=new_row.keys())
    
    append_df = pd.DataFrame(new_row)

    if log_df.empty:
        log_df = append_df
    else:
        log_df = pd.concat([log_df, append_df], ignore_index=True).reset_index(drop=True)

    log_df.to_csv(logfile, index=False)
