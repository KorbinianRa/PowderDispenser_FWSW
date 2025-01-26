"""
This module defines the PowderDispenseController class which manages operations related to powder dispensing.
It includes methods to operate the scale, mixer, and pumps based on pre-defined calibration parameters,
and execute sequences for dispensing, flushing, draining, and more.

Classes:
    PowderDispenseController - A controller to manage dispensing operations including scale and mixer functions.
"""
import serial
import serial.tools.list_ports
import time
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
from scipy import stats
from .utils import get_config, read_logfile, write_to_logfile, list_serial_ports, save_config

class PowderDispenseController:
    """
    Initializes the PowderDispenseController with the given serial port and configuration settings.
    Sets up the necessary hardware connections and calibration parameters for powder dispensing operations.

    Parameters:
        ser_port (str): The name of the serial port to connect to the hardware.
        baud_rate (int): The baud rate for serial communication (default: 115200).
        mixTime (float): Default mixing time in seconds (default: 10.0).
        drainTime (float): Default draining time in seconds (default: 10.0).
        defAugerType (str, optional): Default auger type (default: '8mm_base').
        defPowderType (str, optional): Default powder type (default: 'dishwasher_salt').
        config_file (str): Path to the configuration file (default: 'config.json').
    """
    def __init__(self, ser_port, baud_rate=115200, mixTime=10.0, drainTime=10.0, defAugerType=None, defPowderType=None, config_file='config.json') -> None:
        # Initialize the serial connection to the Arduino.
        self.ser = serial.Serial(ser_port, baud_rate)
        print(f"Serial port {ser_port} opened at baud rate {baud_rate}")

        # Wait for the Arduino to signal readiness.
        self.wait_for_arduino()

        # Load the configuration file and store settings.
        self.config_file = config_file
        self.powder_config = get_config(config_file)

        # Initialize scale and stepper states.
        self.isScaleOn = True
        self.isStepperOn = True
        self.disableStepper()  # Ensure stepper motor is disabled initially.
        self.scaleOff()  # Ensure scale is powered off initially.

        # Set default values for operational parameters.
        self.DEFAULT_augerType = defAugerType or '8mm_base'
        self.DEFAULT_powderType = defPowderType or 'dishwasher_salt'
        self.DEFAULT_filterType = 'EWMA'
        self.DEFAULT_reps = self.powder_config['default_constants']['DEFAULT_REPS']
        self.DEFAULT_samples = self.powder_config['default_constants']['DEFAULT_SAMPLES']
        self.DEFAULT_timeout = self.powder_config['default_constants']['DEFAULT_TIMEOUT']
        self.DEFAULT_direction = self.powder_config['default_constants']['DEFAULT_DISPENSE_DIR']
        self.DEFAULT_flushVolume = 1

        # Set default operational times and pin configurations.
        self.drainTime = drainTime
        self.mixTime = mixTime
        self.flushTime = 1
        self.flushPin = 12

        # Load calibration parameters.
        self.scaleSinglePointCal = self.powder_config['calibration']['scaleSinglePointCal']
        self.numMeas = self.powder_config['constants']['numMeas']
        self.dispenseDir = self.powder_config['constants']['dispenseDir']
        self.decimal = self.powder_config['constants']['decimal']

        # Extract calibration weights from configuration.
        self.calWeights = self.powder_config['calibration']['weights']
        self.calWeights_values = [weight['value'] for weight in self.calWeights]

        # Ensure a logs directory exists for logging operations.
        if not os.path.exists('logs'):
            os.makedirs('logs')

        # Initialize a new log file for this session.
        now = datetime.datetime.now()
        self.log_file = f"logs/log_{now.strftime('%d%m%Y_%H%M%S')}.csv"
        log_df = pd.DataFrame(columns=['desired amount', 'measured amount', '# of steps', 'filter type'])
        log_df.to_csv(self.log_file, index=False)

    ### COMMS #####################
    def send_to_arduino(self, send_str):
        """
        Sends a specified string to the connected Arduino device over the serial port.

        Parameters:
            send_str (str): The command string to send to the Arduino.
        """
        self.ser.write(send_str.encode('utf-8'))  # Encode and send the string.

    def recv_from_arduino(self, timeout=None):
        """
        Receives a string from the Arduino device over the serial port with an optional timeout.

        Parameters:
            timeout (int, optional): Maximum time in seconds to wait for a response.

        Returns:
            str: The string received from the Arduino.

        Raises:
            TimeoutError: If no response is received within the specified timeout.
        """
        timeout = timeout or self.DEFAULT_timeout  # Use default timeout if none is provided.
        start_marker = 60  # ASCII code for '<'.
        end_marker = 62    # ASCII code for '>'.
        start_time = time.time()
        ck = ""  # Buffer to store the received string.

        while time.time() - start_time < timeout:
            # Wait for the start marker.
            while ord(self.ser.read()) != start_marker:
                pass

            # Read characters until the end marker is encountered.
            while ord(self.ser.read()) != end_marker:
                char = self.ser.read().decode("utf-8")
                ck += char
            return ck

        raise TimeoutError("Arduino did not respond within timeout. Try resetting the device.")

    def wait_for_arduino(self):
        """
        Waits for a readiness message from the Arduino indicating it is ready to receive commands.
        This function is essential during initialization to ensure the Arduino is fully booted.
        """
        msg = ""
        while "Ready to push powder, baby!" not in msg:
            while self.ser.in_waiting == 0:  # Wait until there is data in the serial buffer.
                pass
            msg = self.recv_from_arduino()  # Read the message from Arduino.
            print(msg)  # Print the message to confirm readiness.

    def clear_serial_buffer(self):
        """
        Clears the serial buffer to ensure there are no lingering data packets before sending a new command.
        This is important for maintaining the integrity of the command sequences sent to the Arduino.
        """
        self.ser.reset_input_buffer()  # Clear the input buffer.

    def run_command(self, command_str):
        """
        Sends a command string to the connected hardware through the serial interface.
        Designed to control the hardware operations such as turning on the scale, mixing, or dispensing.

        Parameters:
            command_str (str): The command string formatted specifically for the hardware.
        """
        self.clear_serial_buffer()  # Clear any residual data in the serial buffer.
        self.send_to_arduino(command_str)  # Send the command string to the Arduino.
        print(f"Sent from PC -- COMMAND -- {command_str}")  # Log the sent command.

        # Wait for and print the response from Arduino.
        while self.ser.in_waiting == 0:
            pass
        response = self.recv_from_arduino()
        print(f"Reply Received: {response}")



### POWDERS ################################
    def get_raw(self):
        """
        Requests and retrieves a raw analog-to-digital converter (ADC) reading from the Arduino.

        Returns:
            float: The raw ADC value as a float, representing the analog signal level detected by the Arduino.
        """
        msg = ""
        # Loop until a message containing "ADC" is received.
        while "ADC" not in msg:
            while self.ser.in_waiting == 0:  # Wait for data in the Serial buffer.
                pass
            msg = self.recv_from_arduino()  # Read the message from Arduino.
            if "ADC" in msg:
                try:
                    raw_data = msg.split(':')[1]  # Extract the data after the "ADC:" prefix.
                    raw_val = float(raw_data.split(',')[0])  # Parse the first value as a float.
                    return raw_val
                except (IndexError, ValueError) as e:
                    # Handle cases where the message format is unexpected or invalid.
                    print(f"Error parsing ADC from message: {msg}")
                    print(f"Exception: {e}")
                    return None
            else:
                print(f"Received message does not contain 'ADC:' {msg}")  # Log unexpected messages.
        return None

    def get_weight(self):
        """
        Requests and retrieves the weight measurement from the Arduino, which is processed and returned in grams.

        Returns:
            float: The weight in grams measured by the Arduino.
        """
        msg = ""
        # Loop until a message containing "Weight" is received.
        while "Weight" not in msg:
            while self.ser.in_waiting == 0:  # Wait for data in the Serial buffer.
                pass
            msg = self.recv_from_arduino()  # Read the message from Arduino.
            if "Weight" in msg:
                try:
                    weight_data = msg.split(':')[1]  # Extract the data after the "Weight:" prefix.
                    weight_val = float(weight_data.split(',')[0])  # Parse the first value as a float.
                    return weight_val
                except (IndexError, ValueError) as e:
                    # Handle cases where the message format is unexpected or invalid.
                    print(f"Error parsing weight from message: {msg}")
                    print(f"Exception: {e}")
                    return None
            else:
                print(f"Received message does not contain 'Weight:' {msg}")  # Log unexpected messages.
        return None

### CONTROL FUNCTIONS ##############################
    def set_mixTime(self, mixTime):
        """
        Sets the mixing time for the controller.

        Parameters:
            mixTime (float): Duration in seconds for which the mixer should operate.
        """
        self.mixTime = mixTime  # Update the mixing time.

    def set_drainTime(self, drainTime):
        """
        Sets the draining time for the controller.

        Parameters:
            drainTime (float): Duration in seconds for which the draining operation should run.
        """
        self.drainTime = drainTime  # Update the draining time.

    def set_default_augerType(self, augerType):
        """
        Sets the default auger type for the dispensing operations.

        Parameters:
            augerType (str): The default auger type to be used.
        """
        self.DEFAULT_augerType = augerType  # Update the default auger type.

    def set_default_powderType(self, powderType):
        """
        Sets the default powder type for the dispensing operations.

        Parameters:
            powderType (str): The default powder type to be used.
        """
        self.DEFAULT_powderType = powderType  # Update the default powder type.

    def set_default_filterType(self, filterType):
        """
        Sets the default filter type for the weight measurements.

        Parameters:
            filterType (str): The default filter type to be used.
        """
        self.DEFAULT_filterType = filterType  # Update the default filter type.

### Single Control Functions
    ## Dispense controller functions
    def dispense(self, amount_or_steps, direction=None, runSteps=False, augerType=None, powderType=None):
        """
        Controls the dispenser to dispense a specified amount or number of steps of powder.

        Parameters:
            amount_or_steps (float): The amount of powder to dispense in grams or the number of steps for the stepper motor.
            direction (str, optional): The direction to dispense, either 'in' or 'out'.
            runSteps (bool, optional): If True, the input is treated as the number of steps; if False, as the amount in grams.
            augerType (str, optional): The type of auger to use for the operation.
            powderType (str, optional): The type of powder to be dispensed.
        """
        # Use defaults if no specific auger or powder type is provided.
        augerType = augerType or self.DEFAULT_augerType
        powderType = powderType or self.DEFAULT_powderType
        direction = direction or self.dispenseDir

        if runSteps:
            # Use the specified number of steps directly.
            neededSteps = amount_or_steps
        else:
            # Calculate the number of steps based on the desired amount and calibration factor.
            augCalFactor = self.powder_config['calibration']['augers'][augerType][powderType]
            neededSteps = amount_or_steps / augCalFactor

        # Send the dispense command to the Arduino.
        self.run_command(f"<Dispense,{neededSteps},{direction}>")

    def enableStepper(self):
        """
        Enables the stepper motor, allowing it to be used for dispensing operations.
        """
        if not self.isStepperOn:  # Only enable if it is not already on.
            self.run_command(f"<DispenserOn>")
            self.isStepperOn = True

    def disableStepper(self):
        """
        Disables the stepper motor, stopping its operations to ensure safety and conserve power.
        """
        if self.isStepperOn:  # Only disable if it is currently on.
            self.run_command(f"<DispenserOff>")
            self.isStepperOn = False

## Scale controller functions
    def measRaw(self, avgReadingSamples=100, filterType=None):
        """
        Measures and returns the raw sensor data from the scale, applying an optional filter.

        Parameters:
            avgReadingSamples (int, optional): The number of readings to average for noise reduction.
            filterType (str, optional): The filter type to apply for smoothing the sensor data.

        Returns:
            float: The raw sensor data after optional filtering.
        """
        filterType = filterType or self.DEFAULT_filterType  # Use the default filter if none is provided.
        self.run_command(f"<ADC,{avgReadingSamples},{filterType}>")  # Send ADC command to Arduino.
        adc_val = self.get_raw()  # Retrieve the raw ADC value.
        return adc_val

    def measWeight(self, avgReadingSamples=100, filterType=None):
        """
        Measures and returns the calibrated weight from the scale after applying the necessary filtering and averaging.

        Parameters:
            avgReadingSamples (int, optional): The number of readings to average for noise reduction.
            filterType (str, optional): The type of filtering to apply.

        Returns:
            float: The weight measured by the scale, processed through the defined filters.
        """
        filterType = filterType or self.DEFAULT_filterType  # Use the default filter if none is provided.
        self.run_command(f"<Meas,{avgReadingSamples},{filterType}>")  # Send weight measurement command.
        weight_val = self.get_weight()  # Retrieve the weight value from Arduino.
        return weight_val

    def scaleOn(self, settle_time=5):
        """
        Turns on the scale and waits for it to settle.
        Only turns on the scale if it is not already on, to prevent redundant operations.

        Parameters:
            settle_time (int, optional): Time in seconds to wait after turning on the scale. Defaults to 5 seconds.
        """
        if not self.isScaleOn:  # Only power on the scale if it is currently off.
            self.run_command(f"<ScaleOn>")
            self.isScaleOn = True
            time.sleep(settle_time)  # Allow time for the scale to stabilize.

    def scaleOff(self):
        """
        Turns off the scale. 
        Only turns off the scale if it is currently on, to prevent redundant operations.
        """
        if self.isScaleOn:  # Only power off the scale if it is currently on.
            self.run_command(f"<ScaleOff>")
            self.isScaleOn = False

    def tare(self):
        """
        Tares the scale, setting the current weight as the zero reference point.
        """
        self.run_command(f"<Tare>")  # Send the tare command to Arduino.

## Mixer controller functions
    def runPump(self, pump, volume=None, time=None):
        """
        Operates a specified pump to dispense a set volume or run for a set time.
        Determines the operation duration based on calibration parameters or directly uses the specified time.

        Parameters:
            pump (str): Identifier for the pump (e.g., 'Flush' or 'Drain').
            volume (float, optional): Volume to dispense. If provided, time is calculated using calibration parameters. Defaults to None.
            time (float, optional): Time in seconds to run the pump. Used if volume is not provided. Defaults to None.
        """
        pump_pin = self.powder_config['calibration']['pumps'][pump]['pin']  # Get the pump's control pin.
        if volume is not None and volume > 0:
            # Calculate the pump runtime based on the calibration parameters.
            a = self.powder_config['calibration']['pumps'][pump]['a']
            b = self.powder_config['calibration']['pumps'][pump]['b']
            pump_time = a * volume + b
        elif time is not None and time > 0:
            # Use the specified time if no volume is provided.
            pump_time = time
        else:
            pump_time = 0

        if pump_time > 0:
            # Send the command to run the pump for the calculated or specified time.
            self.run_command(f"<Pump,{pump_pin},{pump_time}>")

    def runMixer(self, duration=None):
        """
        Runs the mixer for a specified duration.
        Uses a default duration if none is provided.

        Parameters:
            duration (float, optional): Time in seconds to run the mixer. Defaults to the configured mixing time.
        """
        duration = duration or self.mixTime  # Use the default mixing time if no duration is provided.
        self.run_command(f"<Mix,{duration}>")  # Send the mixer command to Arduino.

    def runDrain(self, duration=None):
        """
        Runs the draining operation for a specified duration.
        Uses a default duration if none is provided.

        Parameters:
            duration (float, optional): Time in seconds to drain. Defaults to the configured draining time.
        """
        duration = duration or self.drainTime  # Use the default draining time if no duration is provided.
        self.run_command(f"<Drain,{duration}>")  # Send the drain command to Arduino.

    def runFlush(self, volume=None, time=None):
        """
        Runs a flushing operation using the pump to add liquid to the dispensing system.
        Can operate based on volume or time.

        Parameters:
            volume (float, optional): Volume to flush through the system. Defaults to None.
            time (float, optional): Time in seconds to run the flush. Defaults to None.
        """
        self.runPump('Flush', volume, time)  # Use the pump to perform the flushing operation.

### Sequence Control Functions
    def purge_dispenser(self):
        """
        Purges the powder dispenser system to clean and prepare it for new dispensing cycles.
        Includes steps such as enabling the stepper, taring the scale, and dispensing repeatedly
        to ensure the system is free of residual powder.
        """
        self.enableStepper()  # Ensure the stepper motor is enabled.
        self.scaleOn()  # Power on the scale.
        time.sleep(2)  # Wait for the scale to stabilize.
        self.tare()  # Zero the scale.

        weight = self.measWeight()  # Measure the current weight.
        while weight <= weight + 0.08:
            # Dispense small amounts until no significant powder remains.
            self.dispense(200, direction=self.dispenseDir, runSteps=True)
            time.sleep(3)  # Allow time for the scale to settle.
            weight = self.measWeight()  # Re-measure the weight.

        self.scaleOff()  # Power off the scale.
        self.disableStepper()  # Disable the stepper motor.

    def reset(self, drainTime=None, flushTime=None):
        """
        Resets the dispensing system by running a drain operation followed by a flush.
        This ensures the system is cleaned and ready for the next operation.

        Parameters:
            drainTime (float, optional): The duration to run the drain operation. Defaults to the configured drain time.
            flushTime (float, optional): The duration to run the flush operation. Defaults to the configured flush time.
        """
        drainTime = drainTime or self.drainTime  # Use default drain time if none is provided.
        flushTime = flushTime or self.flushTime  # Use default flush time if none is provided.

        # Perform the drain, flush, and drain sequence.
        self.runDrain(drainTime)
        time.sleep(1)
        self.runFlush(flushTime)
        time.sleep(1)
        self.runDrain(drainTime)
        time.sleep(1)

    def calibrate_auger_seq(self, logfile=None, direction=None, minSteps=1, maxSteps=1, stepInterval=1, augerType=None, powderType=None):
        """
        Performs a calibration sequence for the auger by dispensing and measuring specified amounts
        to determine the calibration factor.

        Parameters:
            logfile (str, optional): Path to the log file for storing calibration results.
            direction (str, optional): Direction of the auger during dispensing (e.g., 'in' or 'out').
            minSteps (int): Minimum number of steps to test during calibration.
            maxSteps (int): Maximum number of steps to test during calibration.
            stepInterval (int): Interval of steps between each calibration test.
            augerType (str, optional): The type of auger being calibrated.
            powderType (str, optional): The type of powder being dispensed during calibration.

        Behavior:
        - Logs calibration results to the specified log file.
        - Updates the calibration factor in the system configuration.
        """
        logfile = logfile or self.log_file  # Use the default log file if none is specified.
        augerType = augerType or self.DEFAULT_augerType  # Use the default auger type if none is provided.
        powderType = powderType or self.DEFAULT_powderType  # Use the default powder type if none is provided.
        direction = direction or self.DEFAULT_direction  # Use the default dispensing direction.

        steps_list = []  # Stores the steps used during calibration.
        measured_amounts = []  # Stores the measured amounts for each step count.

        self.enableStepper()  # Ensure the stepper motor is enabled.

        for steps in range(minSteps, maxSteps + 1, stepInterval):
            # Dispense using the specified number of steps and direction.
            self.dispense(steps, direction=direction, runSteps=True, augerType=augerType, powderType=powderType)
            measuredAmount = float(input(f"Enter the measured amount (in grams) from the scale for {steps} steps: "))

            # Log the steps and measured amount.
            steps_list.append(steps)
            measured_amounts.append(measuredAmount)
            write_to_logfile(logfile, steps=steps, measured_amount=measuredAmount, augerType=augerType, powderType=powderType)

        self.disableStepper()  # Disable the stepper motor after calibration.

        # Perform linear regression to calculate the calibration factor.
        slope, intercept = np.polyfit(steps_list, measured_amounts, 1)
        self.powder_config['calibration']['augers'][augerType][powderType] = slope  # Update the configuration with the new calibration factor.
        save_config(config_file=self.config_file, powder_config=self.powder_config)  # Save the updated configuration.
        print(f"Updated calibration factor for {augerType} with {powderType}: {slope}")

    def calibrate_scale_seq(self, knownWeights=None, numMeas=None):
        """
        Calibrates the scale by measuring known weights and performing a linear regression to determine the calibration factors.

        Parameters:
            knownWeights (list of floats, optional): A list of known weights to be used for calibration.
            numMeas (int, optional): Number of measurements to take for each weight to increase accuracy.

        Behavior:
        - Logs calibration data.
        - Updates the scale calibration parameters in the system configuration.
        """
        numMeas = numMeas or self.numMeas  # Use default measurement count if not specified.
        calibration_data = []  # Store calibration data as a list of tuples (weight, ADC value).

        self.enableStepper()  # Enable the stepper motor to ensure it’s ready for operation.
        self.scaleOn()  # Power on the scale.

        def record_weight(weight):
            """
            Helper function to record the average ADC value for a given weight.
            Parameters:
                weight (float): The known weight in grams.
            """
            totalADC = sum(self.measRaw() for _ in range(numMeas)) / numMeas  # Average ADC value over multiple readings.
            calibration_data.append((weight, totalADC))
            print(f"Recorded {weight} g: {totalADC} (ADC Value)")  # Log the weight and ADC value.

        if knownWeights is None:
            # If no weights are provided, prompt the user to manually record weights.
            print("\nPlace the scale setup on an analytical scale and let it settle. Press a key when ready.")
            input()
            while True:
                print("Remove all weights from the scale. Press a key when ready to record the zero weight measurement.")
                input()
                record_weight(0.0)  # Record the zero-offset value.
                weight = input("Enter the next known weight (g) or 'done' to finish: ")
                if weight.lower() == 'done':
                    break
                try:
                    weight = float(weight)  # Convert input to a float.
                    print(f"Place {weight} g on the scale. Press a key when ready.")
                    input()
                    record_weight(weight)
                except ValueError:
                    print("Invalid input. Please enter a numeric value or 'done'.")
        else:
            # Use the provided list of known weights.
            print("\nPlace the scale setup on an analytical scale and let it settle. Press a key when ready.")
            input()
            for weight in knownWeights:
                print("Remove all weights from the scale. Press a key when ready to record the zero weight measurement.")
                input()
                record_weight(0.0)  # Record the zero-offset value.

                print(f"Place {weight} g on the scale. Press a key when ready.")
                input()
                record_weight(weight)

        self.scaleOff()  # Power off the scale after calibration.
        self.disableStepper()  # Disable the stepper motor.

        # Perform linear regression to calculate the calibration slope and intercept.
        df = pd.DataFrame(calibration_data, columns=["Known Weight (g)", "Measured ADC Value"])
        slope, intercept, r_value, p_value, std_err = stats.linregress(df["Known Weight (g)"], df["Measured ADC Value"])
        df["Slope"], df["Intercept"] = slope, intercept
        df["Regression Equation"] = f"y = {slope:.4f}x + {intercept:.4f}"
        df.to_excel("calibration_data_with_regression.xlsx", index=False)  # Save calibration data to an Excel file.
        print(f"\nCalibration Results:\nSlope: {slope:.4f}\nIntercept: {intercept:.4f}\nRegression Equation: y = {slope:.4f}x + {intercept:.4f}")

        # Update and save the configuration with the new calibration parameters.
        self.update_config_with_calibration(slope, intercept)
        self.write_calibration_log(slope, intercept)

    def dispense_powder_seq(self, desired_amount):
        """
        Performs a sequence of operations to accurately dispense a specified amount of powder by adjusting the amount based on real-time measurements.

        Parameters:
            desired_amount (float): The target amount of powder to dispense in grams.

        Behavior:
        - Uses real-time feedback from the scale to iteratively dispense powder until the desired amount is reached.
        """
        self.scaleOn()  # Power on the scale.
        time.sleep(1)  # Allow the scale to stabilize.
        self.tare()  # Zero the scale.
        time.sleep(1)
        current_amount = self.measWeight()  # Measure the current weight.

        self.enableStepper()  # Enable the stepper motor.
        time.sleep(1)
        initial_dispense_percentage = 0.50  # Start with 50% of the desired amount.
        initial_dispense_amount = desired_amount * initial_dispense_percentage
        self.dispense(initial_dispense_amount, direction=self.dispenseDir, runSteps=False)  # Perform the initial dispense.
        time.sleep(1)

        # Iteratively dispense smaller amounts based on remaining weight.
        while current_amount < desired_amount * 0.80:
            self.dispense(400, direction=self.dispenseDir, runSteps=True)  # Dispense steps in chunks.
            time.sleep(1)
            current_amount = self.measWeight()  # Update the current weight.

        while current_amount < desired_amount * 0.97:
            self.dispense(20, direction=self.dispenseDir, runSteps=True)  # Fine-tune with smaller steps.
            time.sleep(1)
            current_amount = self.measWeight()

        while current_amount < desired_amount * 0.99:
            self.dispense(5, direction=self.dispenseDir, runSteps=True)  # Final small adjustments.
            time.sleep(1)
            current_amount = self.measWeight()

        self.disableStepper()  # Disable the stepper motor.
        self.scaleOff()  # Power off the scale.
        print("Dispensing complete.")

    def sensitivity_test(self, reps=None, samples=None, use_dispenser=False, amount_or_steps=None):
        """
        Conducts a sensitivity test to evaluate the precision and repeatability of the dispensing system.

        Parameters:
            reps (int, optional): Number of repetitions for the test. Defaults to the configured default repetitions.
            samples (int, optional): Number of samples to take in each repetition. Defaults to the configured default samples.
            use_dispenser (bool, optional): Whether to use the dispenser for adding weights. Defaults to False.
            amount_or_steps (float, optional): Amount of powder to dispense or number of steps if using the dispenser.
        """
        reps = reps or self.DEFAULT_reps
        samples = samples or self.DEFAULT_samples
        self.enableStepper()
        self.scaleOn()
        print("Starting sensitivity test...\n")

        for r in range(1, reps + 1):
            print(f"Repetition {r}: Resetting system for the next set of samples.")
            self.tare()  # Reset the scale to zero.

            for s in range(1, samples + 1):
                if use_dispenser:
                    # Dispense and measure using the system.
                    self.dispense_powder_seq(desired_amount=amount_or_steps)
                    measured_weight = self.measWeight()
                else:
                    # Manually add weight and measure.
                    print(f"Place sample {s} on the scale.")
                    input("Press Enter when ready.")
                    measured_weight = self.measWeight()

                # Log the measurement for this sample.
                print(f"Measured Weight: {measured_weight:.3f} g")
                write_to_logfile(self.log_file, repetition=r, sample=s, measured_amount=measured_weight)

        self.scaleOff()
        self.disableStepper()
        print("Sensitivity test complete.")