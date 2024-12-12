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
import ast
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
        port (str): The name of the serial port to connect to the hardware.
        config_file (str): Path to the configuration file containing calibration and other operational parameters.
    """
    def __init__(self, ser_port, baud_rate = 115200, mixTime = 10.0, drainTime = 10.0, defAugerType = None, defPowderType = None, config_file = 'config.json') -> None:
        self.ser = serial.Serial(ser_port, baud_rate)
        print(f"Serial port {ser_port} opened at baud rate {str(baud_rate)}")
        self.wait_for_arduino()
        self.config_file = config_file
        self.powder_config = get_config(config_file)
        self.isScaleOn = True
        self.isStepperOn = True
        self.disableStepper()
        self.scaleOff()
        
        self.DEFAULT_augerType = defAugerType or '8mm_base'
        self.DEFAULT_powderType = defPowderType or'dishwasher_salt'
        self.DEFAULT_filterType = 'EWMA'
        self.DEFAULT_reps = self.powder_config['default_constants']['DEFAULT_REPS']
        self.DEFAULT_samples = self.powder_config['default_constants']['DEFAULT_SAMPLES']
        self.DEFAULT_timeout = self.powder_config['default_constants']['DEFAULT_TIMEOUT']
        self.DEFAULT_direction = self.powder_config['default_constants']['DEFAULT_DISPENSE_DIR']
        self.DEFAULT_flushVolume = 1
        
        self.drainTime = drainTime
        self.mixTime = mixTime
        self.flushTime = 10
        self.flushPin = 12
        
        self.scaleSinglePointCal = self.powder_config['calibration']['scaleSinglePointCal']
        self.numMeas = self.powder_config['constants']['numMeas']
        self.dispenseDir = self.powder_config['constants']['dispenseDir']
        self.decimal = self.powder_config['constants']['decimal']
        
        self.calWeights = self.powder_config['calibration']['weights']
        self.calWeights_values = [weight['value'] for weight in self.calWeights]
        
        if not os.path.exists('logs'):
            os.makedirs('logs')

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
        self.ser.write(send_str.encode('utf-8'))

    def recv_from_arduino(self, timeout = None):
        """
        Receives a string from the Arduino device over the serial port with an optional timeout.

        Parameters:
            timeout (int, optional): The maximum time to wait for a response before raising a TimeoutError.

        Returns:
            str: The string received from the Arduino.

        Raises:
            TimeoutError: If no response is received within the specified timeout.
        """
        timeout = 10 #timeout or self.DEFAULT_timeout
        start_marker = 60
        end_marker = 62
        start_time = time.time()
        ck = ""
        x = "z"
        byte_count = -1
        while time.time() - start_time < timeout:
            while ord(x) != start_marker:
                x = self.ser.read()
            while ord(x) != end_marker:
                if ord(x) != start_marker:
                    ck = ck + x.decode("utf-8")
                    byte_count += 1
                x = self.ser.read()
            return ck
        raise TimeoutError("Arduino did not respond within timeout. Try resetting the device.")

    def wait_for_arduino(self):
        """
        Waits for a readiness message from the Arduino indicating it is ready to receive commands.
        This function is essential during initialization to ensure the Arduino is fully booted.
        """
        msg = ""
        while msg.find("Ready to push powder, baby!") == -1:
            while self.ser.in_waiting == 0:
                pass
            msg = self.recv_from_arduino()
            print(msg)

    def clear_serial_buffer(self):
        """
        Clears the serial buffer to ensure there are no lingering data packets before sending a new command.
        This is important for maintaining the integrity of the command sequences sent to the Arduino.
        """
        self.ser.reset_input_buffer()

    def run_command(self, command_str):
        """
        Sends a command string to the connected hardware through the serial interface.
        Designed to control the hardware operations such as turning on the scale, mixing, or dispensing.

        Parameters:
            command (str): The command string formatted specifically for the hardware.
        """
        self.clear_serial_buffer()
        waiting_for_reply = False
        if not waiting_for_reply:
            self.send_to_arduino(command_str)
            print(f"Sent from PC -- COMMAND -- {command_str}")
            waiting_for_reply = True
        if waiting_for_reply:
            while self.ser.in_waiting == 0:
                pass
            data_received = self.recv_from_arduino()
            print(f"Reply Received: {data_received}")
            waiting_for_reply = False
            print("===========")

### POWDERS ################################
    def get_raw(self):
        """
        Requests and retrieves a raw analog-to-digital converter (ADC) reading from the Arduino.

        Returns:
            float: The raw ADC value as a float, representing the analog signal level detected by the Arduino.
        """
        msg = ""
        while msg.find("ADC") == -1:
            while self.ser.in_waiting == 0:
                pass
            msg = self.recv_from_arduino()
            if "ADC" in msg:
                try:
                    raw_data = msg.split(':')[1]
                    raw_val = float(raw_data.split(',')[0])
                    return raw_val
                except (IndexError, ValueError) as e:
                    print(f"Error parsing ADC from message: {msg}")
                    print(f"Exception: {e}")
                    return None  
            else:
                print(f"Received message does not contain 'ADC:' {msg}")
        return None

    def get_weight(self):
        """
        Requests and retrieves the weight measurement from the Arduino, which is processed and returned in grams.

        Returns:
            float: The weight in grams measured by the Arduino.
        """
        msg = ""
        while msg.find("Weight") == -1:
            while self.ser.in_waiting == 0:
                pass
            msg = self.recv_from_arduino()
            # Check if the message contains the expected 'Weight:' prefix
            if "Weight" in msg:
                try:
                    weight_data = msg.split(':')[1]
                    weight_val = float(weight_data.split(',')[0])
                    return weight_val
                except (IndexError, ValueError) as e:
                    print(f"Error parsing weight from message: {msg}")
                    print(f"Exception: {e}")
                    return None  # or handle it in a way that makes sense for your application
            else:
                print(f"Received message does not contain 'Weight:' {msg}")  # Logging the message
        return None
    

### CONTROL FUNCTIONS ##############################
    def set_mixTime(self, mixTime):
        """
        Sets the mixing time for the controller.

        Parameters:
            mixTime (float): Duration in seconds for which the mixer should operate.
        """
        self.mixTime = mixTime

    def set_drainTime(self, drainTime):
        """
        Sets the draining time for the controller.

        Parameters:
            drainTime (float): Duration in seconds for which the draining operation should run.
        """
        self.drainTime = drainTime

    def set_default_augerType(self, augerType):
        """
        Sets the default auger type for the dispensing operations.

        Parameters:
            augerType (str): The default auger type to be used.
        """
        self.DEFAULT_augerType = augerType

    def set_default_powderType(self, powderType):
        """
        Sets the default powder type for the dispensing operations.

        Parameters:
            powderType (str): The default powder type to be used.
        """
        self.DEFAULT_powderType = powderType

    def set_default_filterType(self, filterType):
        """
        Sets the default filter type for the weight measurements.

        Parameters:
            filterType (str): The default filter type to be used.
        """
        self.DEFAULT_filterType = filterType

### Single Control Functions
    ## Dispense controller functions
    def dispense(self, amount_or_steps, direction = None, runSteps=False, augerType=None, powderType=None):
        """
        Controls the dispenser to dispense a specified amount or number of steps of powder.

        Parameters:
            amount_or_steps (float): The amount of powder to dispense in grams or the number of steps for the stepper motor.
            direction (str, optional): The direction to dispense, either 'in' or 'out'.
            runSteps (bool, optional): If True, the input is treated as the number of steps; if False, as the amount in grams.
            augerType (str, optional): The type of auger to use for the operation.
            powderType (str, optional): The type of powder to be dispensed.
        """
        augerType = augerType or self.DEFAULT_augerType
        powderType = powderType or self.DEFAULT_powderType
        direction = direction or self.dispenseDir
        
        if runSteps:
            # If runSteps is True, use the amount_or_steps directly as steps
            neededSteps = amount_or_steps
        else:
            # If runSteps is False, calculate the needed steps from the desired amount
            augCalFactor = self.powder_config['calibration']['augers'][augerType][powderType]
            neededSteps = amount_or_steps / augCalFactor
        
        # Run the command with the calculated or provided steps
        self.run_command(f"<Dispense,{neededSteps},{direction}>")

    def enableStepper(self):
        """
        Enables the stepper motor, allowing it to be used for dispensing operations.
        """
        if self.isStepperOn == False:
            self.run_command(f"<DispenserOn>")
            self.isStepperOn = True

    def disableStepper(self):
        """
        Disables the stepper motor, stopping its operations to ensure safety and conserve power.
        """
        if self.isStepperOn == True:
            self.run_command(f"<DispenserOff>")
            self.isStepperOn = False

    ## Scale controller functions
    def measRaw(self, avgReadingSamples = 100, filterType = None):
        """
        Measures and returns the raw sensor data from the scale, applying an optional filter.

        Parameters:
            avgReadingSamples (int, optional): The number of readings to average for noise reduction.
            filterType (str, optional): The filter type to apply for smoothing the sensor data.

        Returns:
            float: The raw sensor data after optional filtering.
        """
        filterType = filterType or self.DEFAULT_filterType
        self.run_command(f"<ADC,{avgReadingSamples},{filterType}>")
        adc_val = self.get_raw()
        return adc_val
    
    def measWeight(self, avgReadingSamples = 100, filterType = None):
        """
        Measures and returns the calibrated weight from the scale after applying the necessary filtering and averaging.

        Parameters:
            avgReadingSamples (int, optional): The number of readings to average for noise reduction.
            filterType (str, optional): The type of filtering to apply.

        Returns:
            float: The weight measured by the scale, processed through the defined filters.
        """
        filterType = filterType or self.DEFAULT_filterType
        self.run_command(f"<Meas,{avgReadingSamples},{filterType}>")
        weight_val = self.get_weight()
        return weight_val

    def scaleOn(self, settle_time = 5):
        """
        Turns on the scale and waits for it to settle. 
        Only turns on the scale if it is not already on, to prevent redundant operations.

        Parameters:
        settle_time (int, optional): Time in seconds to wait after turning on the scale. Defaults to 5 seconds.
        """
        if self.isScaleOn == False:
            self.run_command(f"<ScaleOn>")
            self.isScaleOn = True
            time.sleep(settle_time)
        
    def scaleOff(self):
        """
        Turns off the scale. 
        Only turns off the scale if it is currently on, to prevent redundant operations.
        """
        if self.isScaleOn == True:
            self.run_command(f"<ScaleOff>")
            self.isScaleOn = False

    def tare(self):
        """
        Tares the scale, setting the current weight as the zero reference point.
        """

        self.run_command(f"<Tare>")

    ## Mixer controller functions
    def runPump(self, pump, volume=None, time=None):
        """
        Operates a specified pump to dispense a set volume or run for a set time.
        Determines the operation duration based on calibration parameters or directly uses the specified time.

        Parameters:
            pump (str): Identifier for the pump.
            volume (float, optional): Volume to dispense. If provided, time is calculated based on calibration. Defaults to None.
            time (int, optional): Time in seconds to run the pump. Used if volume is not provided. Defaults to None.
        """
        pump_pin = self.powder_config['calibration']['pumps'][pump]['pin']
        if volume is not None and volume > 0:
            a = self.powder_config['calibration']['pumps'][pump]['a']
            b = self.powder_config['calibration']['pumps'][pump]['b']
            pump_time = a * volume + b
        elif time is not None and time > 0:
            pump_time = time
        else:
            pump_time = 0
        if pump_time > 0:
            self.run_command(f"<Pump,{pump_pin},{pump_time}>")

    def runMixer(self, duration = None):
        """
        Runs the mixer for a specified duration. 
        Uses a default duration if none is provided.

        Parameters:
            duration (int, optional): Time in seconds to run the mixer. Defaults to configured mixing time.
        """
        duration = duration or self.mixTime
        self.run_command(f"<Mix,{duration}>")

    def runDrain(self, duration = None):
        """
        Runs the draining operation for a specified duration.
        Uses a default duration if none is provided.

        Parameters:
            duration (int, optional): Time in seconds to drain. Defaults to configured draining time.
        """
        duration = duration or self.drainTime
        self.run_command(f"<Drain,{duration}>")

    def runFlush(self, volume = None, time = None):
        """
        Runs a flushing operation using the pump to clear out the dispensing system.
        Can operate based on volume or time.

        Parameters:
            volume (float, optional): Volume to flush through the system. Defaults to None.
            time (int, optional): Time in seconds to run the flush. Defaults to None.
        """
        self.runPump('Flush', volume, time)

### Sequence Control Functions
    def purge_dispenser(self):
        """
        Purges the powder dispenser system to clean and prepare it for new dispensing cycles. 
        This includes a series of steps such as enabling the stepper, taring the scale, and dispensing actions.

        Effectively cleans the system by repeated dispensing and weighing to ensure the dispenser is free from any residual powders.
        """
        self.enableStepper()
        self.scaleOn()
        time.sleep(2)
        self.tare()
        weight = self.measWeight()
        while weight <= weight + 0.08:
            self.dispense(200, direction = self.dispenseDir,runSteps = True)
            time.sleep(3)
            weight = self.measWeight()
        self.scaleOff()
        self.disableStepper()

    def reset(self, drainTime = None, flushTime = None):
        """
        Resets the dispensing system by running a drain operation followed by a flush.

        Parameters:
            drainTime (float, optional): The duration to run the drain operation. Uses the controller's configured drain time by default.
        """
        drainTime = drainTime or self.drainTime
        flushTime = flushTime or self.flushTime
        self.runDrain(drainTime)
        time.sleep(1)
        self.runFlush(flushTime)
        time.sleep(1)
        self.runDrain(drainTime)
        time.sleep(1)

    def calibrate_auger_seq(self, logfile = None, direction = None, minSteps = 1, maxSteps = 1, stepInterval = 1, augerType=None, powderType=None):
        """
        Performs a calibration sequence for the auger by dispensing and measuring specified amounts to determine the calibration factor.

        Parameters:
            logfile (str, optional): The path to the logfile where the results are stored.
            direction (str, optional): The direction of the auger during the dispensing.
            minSteps (int): The minimum number of steps to test.
            maxSteps (int): The maximum number of steps to test.
            stepInterval (int): The interval of steps between tests.
            augerType (str, optional): The type of auger being calibrated.
            powderType (str, optional): The type of powder being used for the calibration.

        The function logs all results and updates the calibration factor in the system configuration.
        """

        logfile = logfile or self.log_file
        augerType = augerType or self.default_augerType
        powderType = powderType or self.default_powderType
        direction = direction or self.DEFAULT_direction
        steps_list = []
        measured_amounts = []
        self.enableStepper()
        
        for steps in range(minSteps, maxSteps + 1, stepInterval):
            self.dispense(steps, direction = direction, runSteps=True, augerType=augerType, powderType=powderType)
            measuredAmount = float(input(f"Enter the measured amount(in g without unit, ex. '0.023') from the scale for {steps} steps: "))
            steps_list.append(steps)
            measured_amounts.append(measuredAmount)
            write_to_logfile(logfile, steps=steps, measured_amount=measuredAmount, augerType=augerType, powderType=powderType)
        self.disableStepper()
        slope, intercept = np.polyfit(steps_list, measured_amounts, 1)
        self.powder_config['calibration']['augers'][augerType][powderType] = slope
        save_config(config_file = self.config_file, powder_config = self.powder_config)
        print(f"Updated calibration factor for {augerType} with {powderType}: {slope}")

    def calibrate_scale_seq(self, knownWeights = None, numMeas = None):
        """
        Calibrates the scale by measuring known weights and performing a linear regression to find the scale factors.

        Parameters:
            knownWeights (list of floats, optional): A list of known weights to be used for calibration.
            numMeas (int, optional): Number of measurements to take for each weight to increase accuracy.

        This function logs the calibration data and updates the scale calibration parameters in the system configuration.
        """
        numMeas = numMeas or self.numMeas
        calibration_data = []
        self.enableStepper()
        self.scaleOn()
        def record_weight(weight):
            totalADC = sum(self.measRaw() for _ in range(numMeas)) / numMeas
            calibration_data.append((weight, totalADC))
            print(f"Recorded {weight} g: {totalADC} (ADC Value)")
        if knownWeights is None:
            print("\nPlace scale setup on top of analytical scale and let it settle. Press a key when ready.")
            input()
            while True:
                print("Remove all weights from the scale. Press a key when ready to record the zero weight measurement.")
                input()
                record_weight(0.0)
                weight = input("Enter the next known weight (g) or 'done' to finish: ")
                if weight.lower() == 'done':
                    break
                try:
                    weight = float(weight)
                    print(f"Place {weight} g on the scale. Press a key when ready.")
                    input()
                    record_weight(weight)
                except ValueError:
                    print("Invalid input. Please enter a numeric value or 'done'.")
        else:
            print("\nPlace scale setup on top of analytical scale and let it settle. Press a key when ready.")
            input()
            for weight in knownWeights:
                print("Remove all weights from the scale. Press a key when ready to record the zero weight measurement.")
                input()
                record_weight(0.0)

                print(f"Place {weight} g on the scale. Press a key when ready.")
                input()
                record_weight(weight)
        self.scaleOff()
        self.disableStepper()
        df = pd.DataFrame(calibration_data, columns=["Known Weight (g)", "Measured ADC Value"])
        slope, intercept, r_value, p_value, std_err = stats.linregress(df["Known Weight (g)"], df["Measured ADC Value"])
        df["Slope"], df["Intercept"] = slope, intercept
        df["Regression Equation"] = f"y = {slope:.4f}x + {intercept:.4f}"
        df.to_excel("calibration_data_with_regression.xlsx", index=False)
        print(f"\nCalibration Results:\nSlope: {slope:.4f}\nIntercept: {intercept:.4f}\nRegression Equation: y = {slope:.4f}x + {intercept:.4f}")
        self.update_config_with_calibration(slope, intercept)
        self.write_calibration_log(slope, intercept)

    def dispense_powder_seq(self, desired_amount):
        """
        Performs a sequence of operations to accurately dispense a specified amount of powder by adjusting the amount based on real-time measurements.

        Parameters:
            desired_amount (float): The target amount of powder to dispense.

        This function continuously adjusts the dispense amount based on the scale feedback to achieve precise dispensing.
        """
        self.scaleOn()
        time.sleep(1)
        self.tare()
        time.sleep(1)
        self.tare()
        time.sleep(1)
        current_amount = self.measWeight()
        time.sleep(1)
        current_amount = self.measWeight()
        time.sleep(1)
        
        self.enableStepper()
        time.sleep(1)
        initial_dispense_percentage = 0.50
        initial_dispense_amount = desired_amount * initial_dispense_percentage
        self.dispense(initial_dispense_amount, direction = self.dispenseDir, runSteps = False)
        time.sleep(1)

        # while current_amount < initial_dispense_amount:
        #     remaining_amount = desired_amount - current_amount
        #     self.dispense(remaining_amount, direction = self.dispenseDir, runSteps = False)
        #     time.sleep(2)
        #     current_amount = self.measWeight()
        #     print(current_amount)
        #     write_to_logfile(
        #         self.log_file,
        #         desired_amount = current_amount,
        #         measured_amount = current_amount,
        #         augerType = self.DEFAULT_augerType,
        #         powderType = self.DEFAULT_powderType,
        #         filterType = self.DEFAULT_filterType
        #     )
        while current_amount < desired_amount * 0.80:
            self.dispense(400, direction = self.dispenseDir, runSteps = True)
            time.sleep(1)
            current_amount = self.measWeight()
            print(current_amount)
            write_to_logfile(
                self.log_file,
                desired_amount = current_amount,
                measured_amount = current_amount,
                augerType = self.DEFAULT_augerType,
                powderType = self.DEFAULT_powderType,
                filterType = self.DEFAULT_filterType
            )
        while current_amount < desired_amount * 0.97:
            self.dispense(20, direction = self.dispenseDir, runSteps = True)
            time.sleep(1)
            current_amount = self.measWeight()
            print(current_amount)
            write_to_logfile(
                self.log_file,
                desired_amount = current_amount,
                measured_amount = current_amount,
                augerType = self.DEFAULT_augerType,
                powderType = self.DEFAULT_powderType,
                filterType = self.DEFAULT_filterType
            )
        while current_amount < desired_amount * 99:
            self.dispense(5, direction = self.dispenseDir , runSteps = True)
            time.sleep(1)
            current_amount = self.measWeight()
            print(current_amount)
            write_to_logfile(
                self.log_file,
                desired_amount = current_amount,
                measured_amount = current_amount,
                augerType = self.DEFAULT_augerType,
                powderType = self.DEFAULT_powderType,
                filterType = self.DEFAULT_filterType
            )
        self.disableStepper()
        # Log the data
        write_to_logfile(
            self.log_file,
            desired_amount = current_amount,
            measured_amount = current_amount,
            augerType = self.DEFAULT_augerType,
            powderType = self.DEFAULT_powderType,
            filterType = self.DEFAULT_filterType
        )
        print("Dispensing complete.")

    def sensitivity_test(self, reps = None, samples = None, use_dispenser = False, amount_or_steps = None):
        """
        Conducts a sensitivity test to evaluate the precision and repeatability of the dispensing system across multiple repetitions.

        Parameters:
            reps (int, optional): Number of repetitions for the test.
            samples (int, optional): Number of samples to take in each repetition.
            use_dispenser (bool, optional): Whether to use the dispenser for adding weights or manually place them.
            amount_or_steps (float, optional): The amount of powder to dispense or the steps if using the dispenser.

        Logs all measurements and provides a detailed report on the system's sensitivity.
        """
        reps = reps or self.DEFAULT_reps
        samples = samples or self.DEFAULT_samples
        self.enableStepper()
        self.scaleOn()
        print("Starting sensitivity test...\n")
        self.tare()
        for r in range(1, reps + 1):
            print(f"On repetition {r}")
            print("Setup scale with no weight on it. Press a key when ready.")
            input()
            self.tare()
            known_weights = [0] * (samples + 1)
            measured_weights = [0] * (samples + 1)
            acc_known_weight = 0
            for s in range(1, samples + 1):
                if use_dispenser:
                    print(f"Dispensing sample {s} amount or steps.")
                    self.dispense_powder_seq(desired_amount = amount_or_steps)
                    print("Please let the scale settle...")
                    time.sleep(10)
                    measured_weights[s] = self.measWeight()
                    print(f"Measured weight on scale: {measured_weights[s]:.{self.decimal}f} g")
                    acc_known_weight += amount_or_steps
                    known_weights[s] = acc_known_weight  # assuming each dispense amount is added cumulatively
                    print(f"Accumulated dispensed weight: {acc_known_weight:.{self.decimal}f} g")
                else:
                    print(f"Place known weight ({s}) on scale.\nPress a key when weight is in place and stable.")
                    input()
                    known_weights[s] = float(input("Please enter the weight, without the unit, which was added on the scale (for example '4.25', leave out 'g'): "))
                    print(f"{known_weights[s]:.{self.decimal}f} g")
                    print("Please let the scale settle...")
                    time.sleep(10)
                    measured_weights[s] = self.measWeight()
                    print(f"Measured weight on scale: {measured_weights[s]:.{self.decimal}f} g")
                    acc_known_weight += known_weights[s]
                    print(f"Accumulated known weights on scale: {acc_known_weight:.{self.decimal}f} g")
                print(f"Sensitivity of this run: {acc_known_weight - measured_weights[s]:.{self.decimal}f} g")
                write_to_logfile(
                    self.log_file,
                    desired_amount=known_weights[s],
                    measured_amount=measured_weights[s],
                    steps=s if use_dispenser else None,
                    augerType=self.DEFAULT_augerType,
                    powderType=self.DEFAULT_powderType
                )
                if use_dispenser and s < samples:
                    print("Resetting system for the next sample...")
                    self.runFlush(0.5)
                    self.reset()
        self.scaleOff()
        self.disableStepper()
        print("Sensitivity test complete.")
        
    def stability_test(self, test_duration=30, desired_amount=1):
        """
        Performs a stability test over a specified duration to assess the consistency of the dispensing operations.

        Parameters:
            test_duration (int): The duration in seconds over which to conduct the test.
            desired_amount (float): The amount of powder to repeatedly dispense during the test.

        This function logs all data to assess the stability and repeatability of the dispensing operations.
        """
        test_start_time = time.time()
        now = datetime.datetime.now()
        log_file = f"stability_test_{now.strftime('%Y%m%d_%H%M%S')}_amount_{desired_amount}.csv"
        while (time.time() - test_start_time) <= test_duration:
            print("Adding solvent...")
            self.runFlush(1)
            time.sleep(3)
            self.tare()
            time.sleep(3)
            measured_weight = self.measWeight()
            while measured_weight <= -0.5 or measured_weight >= 0.5:
                self.tare()
                time.sleep(3)
                measured_weight = self.measWeight()
            print("Starting dispense sequence...")
            self.dispense_powder_seq(desired_amount)
            self.disableStepper()
            self.runMixer(5)
            time.sleep(5)
            print("Resetting system for the next measurement...")
            self.runDrain(8)
            current_time = time.time() - test_start_time
            measured_weight = self.measWeight()
            time.sleep(0.5)
            write_to_logfile(log_file, desired_amount=desired_amount, measured_amount=measured_weight, augerType = self.DEFAULT_augerType, powderType = self.DEFAULT_powderType)
            self.scaleOff()
            self.disableStepper()
            print(f"Time: {current_time:.2f}s, Desired Amount: {desired_amount}g, Measured Weight: {measured_weight:.{self.decimal}f} g")
        self.scaleOff()
        self.disableStepper()
        print("Stability test complete. Results saved to '{log_file}'.")

    def accuracy_test(self, use_known_weights=True, known_weights=None, desired_amount=None, reps=None, samples=None):
        """
        Conducts an accuracy test to evaluate how closely the dispensed amounts match the known or desired amounts.

        Parameters:
            use_known_weights (bool): If true, uses provided known weights for testing accuracy.
            known_weights (list of floats, optional): A list of known weights to use if `use_known_weights` is true.
            desired_amount (float, optional): The target amount to test accuracy if not using known weights.
            reps (int, optional): The number of repetitions for the test.
            samples (int, optional): The number of samples in each repetition.

        Logs each test and provides an analysis of the system's accuracy.
        """
        if use_known_weights and not known_weights:
            raise ValueError("Known weights must be provided if use_known_weights is True.")
        if not use_known_weights and not desired_amount:
            raise ValueError("Desired amount must be provided if use_known_weights is False.")
        reps = reps or self.DEFAULT_reps
        samples = samples or self.DEFAULT_samples
        self.enableStepper()
        self.scaleOn()
        now = datetime.datetime.now()
        log_file = f"accuracy_test_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        results = []
        print("Starting accuracy test...\n")
        for r in range(1, reps + 1):
            print(f"On repetition {r}")
            print("Setup scale with no weight on it. Press a key when ready.")
            input()
            self.tare()
            for s in range(1, samples + 1):
                if use_known_weights:
                    print(f"Place known weight ({s}) on scale.\nPress a key when weight is in place and stable.")
                    input()
                    known_weight = float(input("Please enter the weight, without units, currently sitting on the scale (for example '4.25'): "))
                else:
                    print(f"Dispensing powder for sample {s}.")
                    self.dispense_powder_seq(desired_amount)
                    known_weight = desired_amount
                print(f"{known_weight:.{self.decimal}f} g\nPlease let the scale settle...")
                time.sleep(10)
                measured_weight = self.measWeight()
                results.append((r, s, known_weight, measured_weight))
                print(f"Measured weight on scale: {measured_weight:.{self.decimal}f} g")
        self.scaleOff()
        self.disableStepper()
        df = pd.DataFrame(results, columns=["Repetition", "Sample", "Known Weight (g)", "Measured Weight (g)"])
        df.to_csv(log_file, index=False)
        print(f"Accuracy test complete. Results saved to '{log_file}'.")
        
    def log_measurements_by_filter(self, duration=60, rawOn = True):
        """
        Logs weight measurements over a specified duration using different filtering techniques to assess their impact.

        Parameters:
            duration (int): The duration in seconds for which to log measurements.
            rawOn (bool): If true, logs raw sensor data; otherwise, logs processed weight data.

        Collects and logs data to analyze the performance of different filtering methods in real-time.
        """
        filter_types = ['NONE', 'EWMA', 'SMA', 'LPF']
        now = datetime.datetime.now()
        log_file = f"measurements_{now.strftime('%Y%m%d_%H%M%S')}.csv"
        start_time = time.time()

        while (time.time() - start_time) <= duration:
            for filter_type in filter_types:
                if rawOn == False: 
                    measured_weight = self.measWeight(filterType=filter_type)
                else:
                    measured_weight = self.measRaw(filterType=filter_type)
                write_to_logfile(log_file, measured_amount=measured_weight, filterType=filter_type)
                print(f"Logged {measured_weight:.{self.decimal}f} g using {filter_type} filter.")
        print("Measurement logging complete. Results saved to '{log_file}'.")


