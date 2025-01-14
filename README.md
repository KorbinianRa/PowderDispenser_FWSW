# Powder Dispenser Project

## Overview
This subrepository contains all necessary software and firmware components for [the Powder Dispensing and Weighing module project repository](https://github.com/loppe35/PowderDispensing_and_Weighing_Module.git). This includes the source code, configuration files, notebooks, and environment setups. It's designed to provide a comprehensive toolkit for managing and controlling powder dispensation via software interfaces and hardware controllers.

## Contents
- **.vscode**: Contains configuration settings for Visual Studio Code, helpful for setting up a consistent development environment across different setups.
- **config.json**: Central configuration file where system parameters and operational settings are stored.
- **logs**: Directory for storing log files, which are useful for debugging and tracking system performance over time.
- **Notebooks**: Jupyter notebooks that may contain simulations, test scripts, or data analysis related to the powder dispensation processes.
- **PowderDispenserController**: Contains the control logic for managing the hardware aspects of the powder dispenser.
- **PowderDispenserCPP**: C++ modules that interface directly with the hardware or provide computational logic where higher performance is needed.
- **PowderEnv**: Includes scripts or configurations to set up Python virtual environments, ensuring dependency management and isolated runtime.
- **requirements.txt**: Lists all Python dependencies required to run Python scripts and notebooks effectively in the project.
- **LICENSE**: A folder for all the licensing documentation which the project is released under.

## Getting Started
To get started with this project, access the database and download the necessary files. Follow these steps to set up the environment and begin using the project components:
- Setup the environment: Navigate to the PowderEnv directory and follow the setup instructions.
- Install Python dependencies: Execute 'pip install -r requirements.txt' in the command line.

## Configuration
Edit the config.json to match your specific hardware and operational parameters. Detailed information on each configuration parameter can be found within the file, along with some additional information which was used during testing.

## Usage
Instructions on how to run and use the software are as follows:
- Start the controller by navigating to PowderDispenserController and running the appropriate scripts.
- For simulation or additional analysis, refer to the Notebooks directory, here is an example use file which can be used for some of the basic functionalities.

## Contributing
Contributions to this project are welcome. Please ensure to follow the code of conduct and pull request etiquette when contributing.

## License
The software in this directory is released under the MIT License. See the `LICENSE` file for full license text.
