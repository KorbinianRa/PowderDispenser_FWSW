# Firmware and Software Repository for Powder Dispenser Project

## Overview
This repository contains all necessary firmware and software components for the **Powder Dispenser and Weighing Module** project. It serves as the control center, providing:

- **Firmware**: Low-level control of hardware components.
- **Software**: High-level tools for configuration, data analysis, and process control.
- **Examples**: Jupyter notebooks to demonstrate system capabilities and usage.

This repository is structured to facilitate easy installation, usage, and further development.

### Related Repositories
- **[Main Project Repository](https://github.com/loppe35/PowderDispensing_and_Weighing_Module.git)**: The overarching project repository linking hardware and software components.
- **[Hardware Repository](https://github.com/loppe35/PowderDispenser_BuildFiles.git)**: Contains 3D models, schematics, and assembly instructions.


---

## Repository Contents

### **1. Firmware**
Located in the `PowderDispenserCPP` directory:
- **Purpose**: Directly interfaces with the hardware for tasks such as tarring, auger control, and powder dispensation.
- **Implementation**: Written in C++ for performance and compiled for Arduino boards.
- **Setup**:
  1. Install PlatformIO (a modern embedded development environment).
  2. Open the `PowderDispenserCPP` directory as a project in PlatformIO.
  3. Ensure all dependencies specified in `platformio.ini` are resolved.
  4. Compile and upload the firmware to your Arduino board using PlatformIO's interface or command-line tools:
     ```bash
     pio run --target upload
     ```

### **2. Software**
Located in the `PowderDispenserController` directory:
- **Purpose**: Provides Python scripts to control hardware, analyze data, and run tests.
- **Key Files**:
  - `config.json`: Central configuration file for system parameters and operational settings. (Details below)
  - `requirements.txt`: Python dependencies for the project.

### **3. Notebooks**
Located in the `Notebooks` directory:
- **Purpose**: Demonstrate system capabilities and assist in data analysis.
- **Key Features**:
  - Examples of powder dispensation processes.
  - Operation guide with code examples.
  - Introduction to calibration and testing processes.

### **4. Logs**
Located in the `logs` directory:
- Stores system logs, useful for debugging and performance tracking.

### **5. Components and Hardware**
A render depicting the complete system with explanatory labels is provided:
![Full System w. Dummy](https://raw.githubusercontent.com/loppe35/PowderDispenser_BuildFiles/Renders/FullRender.jpg)

Below is a list of essential components required to set up the powder dispensing system.

#### **3D Printable Parts**
These parts are available in the `hardware` submodule as STP and STL files and are essential for constructing the powder dispenser:

- **Load Cell Housing**:
  - Houses and positions the load cell accurately for precise weight measurements, and serves as a rail for the dispensing head.
  - ![Load Cell Housing](https://raw.githubusercontent.com/loppe35/PowderDispenser_BuildFiles/Part_Pictures/LC_Housing.jpg)
  - Here, the unigripper can also be seen, these are the small hooks taht are attached to the load cell to leave a space for the testing cell to rest.

- **Dispensing Head**:
  - Holds the auger mechanism in place and ensures proper alignment, and sits in the 
  - ![Dispenser Head sitting in the Load Cell housing rail](https://raw.githubusercontent.com/loppe35/PowderDispenser_BuildFiles/Part_Pictures/DispHead_onMount.jpg)
  - ![Dispenser Head with needle in the needle rack](https://raw.githubusercontent.com/loppe35/PowderDispenser_BuildFiles/Part_Pictures/DispHead_w_needle.jpg)

- **Syringe Bracket**:
  - Sits around a syringe and is able to hold on the Unigrippers on the load cell.
  - ![Syringe Bracket](https://raw.githubusercontent.com/loppe35/PowderDispenser_BuildFiles/Part_Pictures/SyringeBracket_s.jpg)

- **Base Front and Back**:
  - Provides structural support for the dispenser components. The front also holds the magnetic stirrer and peristaltice pump, while the back holds all the electronics.

- **Back Cover**:
  - Covers up all the electronics for safety, as well as adds a bit to the aesthetics.

- **Mounting Plate**:
  - Serves as a sheet where the different components can be mounted.

- **Magnetic Stirrer Magnet Mount**:
  - Provides structural support for the dispenser components.

- **Dummy Input 3D Printable Components(Optional)**:
  - Dummy Unit Casing Front and Back: 3D Printable parts for a dummy casing holding the peristaltic pump and the relay.
  - ![Dummy Input](https://raw.githubusercontent.com/loppe35/PowderDispenser_BuildFiles/Part_Pictures/Dummy_s.jpg)


#### **Additional Hardware Components**
An overview of additional parts which are required is given below, these are mainly non-3D Printable parts, and some are even optional.

- **Microcontroller (e.g., Arduino)**: Used with the flashed firmware to control low-level system of the module.
- **8mm Auger Mechanism**: Used for precise powder dispensing. This could be modified to another auger size, the system is tested with this size however. Run by a stepper motor.
- **Stepper Motor**: Used to run the auger mechanism.
- **Load Cell**: Used as the measuring components along wiht an ADC, to measure the weiht of the dispensed substance.
- **ADC or Scale unit**: Converts the signal from the load cell to a readible signal for the controller.
- **Drain Pump**: Handles liquid flow during cleaning or other operations. This would be a peristaltic punp operated by a relay.
- **Relay**: Controlled by the microcontroller, the relay is used as a switch to operate the pump.
- **Custom Circuitry**: Interfaces between components like load cells and augers.
- **40x40 Computer fan**: Serves as the active component of the magnetic stirrer, where a the magnetic stirrer magnet mount is mounted on.
- **Dummy Input Components (Optional)**: Additional components are needed if a dummy liquid input is required for testing.
    - **Peristaltic Pump**: Handles the input liquid into the testing chamber.
    - **Pump Relay**: Facilitates the switiching of the peristaltic pump.


Additional information on all the parts can be found in the **[Hardware Repository](https://github.com/loppe35/PowderDispenser_BuildFiles.git)**. Here, some additional pictures of parts and renders is also provided.

---

## Configuration File: `config.json`
The `config.json` file defines the calibration, constants, and default settings for the powder dispenser. It is essential for tailoring the system to your specific hardware setup and operational needs.

### **Key Sections and Parameters**

#### **1. Calibration**
- **Augers**: Defines calibration coefficients for auger mechanisms using different materials (e.g., dishwasher salt).
- **Load Cells**: Contains calibration parameters (slope and intercept) for each load cell used (e.g., 100g, 50g, 20g).
- **Weights**: Predefined calibration weights, including their values and units (e.g., grams).
- **Pumps**: Configurations for connected pumps, including control pin numbers and calibration coefficients for flow rate calculations.

#### **2. Constants**
- **decimal**: Precision for displayed numerical values.
- **mixTime**: Duration for mixing operations (seconds).
- **drainTime**: Time allocated for draining operations (seconds).
- **dispenseDir**: Direction of dispensing (1 for forward, -1 for reverse).
- **scaleSamplerate**: Sampling rate for the scale (in Hz).
- **scaleFilterType**: Type of filter applied to stabilize scale readings (e.g., "EWMA").

#### **3. Default Constants**
- These serve as fallback settings if specific values are not provided elsewhere in the system.
- Examples include default timeout durations, sampling rates, and calibration modes for the scale.

### **Editing the Configuration File**
Modify `config.json` to reflect your hardware and operational requirements:
1. Update the calibration parameters to match the characteristics of your augers, load cells, and pumps.
2. Adjust constants such as `mixTime`, `scaleSamplerate`, and `scaleFilterType` to optimize system performance.
3. Use descriptive comments in the file to ensure clarity and ease of future modifications.

---

## Getting Started

### **1. Acquire and Assemble Components**
To set up the hardware for the **Powder Dispenser and Weighing Module**, follow these steps:

1. **Acquire Components**:
   - Gather the required hardware components, such as the microcontroller, load cells, pumps, and other parts listed in the hardware repository.
   - 3D-print the necessary parts using the provided STL files in the hardware repository.

2. **Assembly**:
   - Use the detailed assembly instructions available in the hardware repository (`PowderDispenser_BuildFiles`) to construct the module.
   - Ensure all components are securely assembled and connections are correctly made.

3. **Verify Assembly**:
   - Double-check all connections and the overall assembly against the provided guide before proceeding with software setup.

### **2. Clone All Required Repositories**
This project is split into multiple repositories to separate hardware and software components. You need to clone the following repositories for complete setup(Only the FWSW Repository has code which needs to be run):

1. **Main Repository**:
   - Provides an overview and links the hardware and software components:
     ```bash
     git clone https://github.com/loppe35/PowderDispensing_and_Weighing_Module.git
     ```

2. **Hardware Repository**:
   - Contains 3D models, schematics, and assembly instructions:
     ```bash
     git clone https://github.com/loppe35/PowderDispenser_BuildFiles.git
     ```

3. **Firmware and Software Repository**:
   - Clone this repository for firmware and software:
     ```bash
     git clone https://github.com/loppe35/PowderDispenser_FWSW.git
     ```


Make sure to clone these repositories into the same parent directory for seamless integration.

### **3. Install Dependencies**
Navigate to the root of the repository and install Python dependencies:
```bash
pip install -r requirements.txt
```

### **4. Compile and Upload Firmware**
Navigate to the `PowderDispenserCPP` directory:
- Open the project in PlatformIO.
- Use the PlatformIO interface or CLI to compile and upload the firmware:
  ```bash
  pio run --target upload
  ```

### **5. Run the System Using Jupyter Notebook**
To start the controller and execute dispensing operations, use the provided `Use_Example.ipynb` notebook located in the `Notebooks` directory. Open the notebook with Jupyter and follow the step-by-step examples to:
- Initialize the dispenser.
- Run calibration routines.
- Execute dispensing operations.

---

## Usage

### **Workflow for Typical Operation**
1. **Set Up Hardware**:
   - Assemble the system using the instructions in the hardware repository.
   - Connect the microcontroller to the PC.
2. **Upload Firmware**:
   - Use PlatformIO to upload the firmware to the microcontroller.
3. **Configure System**:
   - Edit `config.json` to match your hardware setup.
4. **Start Dispensing**:
   - Use the Jupyter notebook `Use_Example.ipynb` to:
     - Initialize the dispenser.
     - Run a dispensing operation.
     - Perform calibration and testing as needed.
5. **Expand**:
    - Use the premade functions to create you own workflow and integrate it with existing system as needed.

### **Testing**
To run tests, use the examples provided in the `Use_Example.ipynb` notebook. These consist of the following, and a snippet is also provided below.
- **Sensitivity Test**: Evaluates the scale's response to small changes in weight.
- **Accuracy Test**: Validates how closely the dispensed weight matches the desired or known weight.
- **Stability Test**: Measures the system's ability to maintain consistent performance over time.
- **Calibration Test**: Determines scale and auger calibration parameters for optimal accuracy.

---

### **Examples**
#### Dispensing Multiple Powders
Here is a simple example on how one could dispense an amount of different predetermined substances, with their respective calibrations, solely relying on the auger (no feedback from the scale).
```python
# Example: Dispensing two powders sequentially
dispenseBot.dispense_powder_seq(desired_amount=0.1, powder_type="Salt")
dispenseBot.dispense_powder_seq(desired_amount=0.05, powder_type="Sugar")
```

#### Single Powder Dispense with Calibration
```python
# Example: Dispensing a single powder with calibration
dispenseBot.calibrate_scale_seq(knownWeights=[0.1, 1.0, 5.0])
dispenseBot.dispense_powder_seq(desired_amount=0.2)
```

#### Performing a Stability Test
```python
# Example: Running a stability test
dispenseBot.stability_test(test_duration=600, desired_amount=0.1)
```

#### Dispensing with Steps and Amount
**Example: Dispensing with Steps**
```python
# Enable the stepper motor
dispenseBot.enableStepper()

# Dispense 1000 steps of powder
dispenseBot.dispense(amount_or_steps=1000, runSteps=True, direction=1)

# Disable the stepper motor
dispenseBot.disableStepper()
```

**Example: Dispensing with Amount**
```python
# Enable the stepper motor
dispenseBot.enableStepper()

# Dispense 0.5 grams of powder
dispenseBot.dispense(amount_or_steps=0.5, runSteps=False, direction=1)

# Disable the stepper motor
dispenseBot.disableStepper()
```

#### Dispensing Cycle
Automate a complete manuel dispensing cycle, including flushing, dispensing, and weighing.
```python
# Example of an automated dispensing cycle
for cycle in range(3):
    print(f"Starting cycle {cycle + 1}")

    # Flush the system
    dispenseBot.runFlush(2)

    # Prepare the scale
    dispenseBot.scaleOn()
    dispenseBot.tare()

    # Dispense powder
    dispenseBot.dispense_powder_seq(desired_amount=0.5)

    # Weigh the dispensed amount
    weight = dispenseBot.measWeight()
    print(f"Measured weight: {weight:.2f} grams")

    # Mix and drain
    dispenseBot.runMixer(5)
    dispenseBot.runDrain(3)

    print(f"Cycle {cycle + 1} complete")
```

Further explanation and additional examples are provided in the `Use_Example.ipynb` notebook.

---

## License

This repository is licensed under the **MIT License**:
- Free to use, modify, and distribute.
- Attribution required.

Refer to the `LICENSE` file for the full terms.

---