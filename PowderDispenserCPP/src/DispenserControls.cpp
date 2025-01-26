#include "DispenserControls.h"

/**
 * Static variable to track whether the dispenser is enabled.
 * - `dispenserEnabled` (bool): True if the dispenser is enabled, false otherwise.
 */
bool DispenserControls::dispenserEnabled = false;

/**
 * Constructor for the DispenserControls class.
 * 
 * Parameters:
 * - `utils` (Utils&): Reference to the utility class for shared functionality.
 */
DispenserControls::DispenserControls(Utils& utils) : utils(utils) {}

/**
 * Sets up the dispenser by configuring its settings and initializing the driver.
 * 
 * Parameters:
 * - `resVar` (int): Resolution setting for the stepper motor (e.g., 2, 4, 8, etc.).
 * 
 * Behavior:
 * - Configures the step resolution mode (currently commented out).
 * - Sets the control mode to serial communication.
 * - Initializes the dispenser driver and sets the current limit.
 * - Disables the dispenser by default.
 */
void DispenserControls::setupDispenser(int resVar) {
    // Uncomment the switch block below to enable resolution configuration if needed.
    /*
    switch (resVar) {
        case 2:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_2; break;
        case 4:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_4; break;
        case 8:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_8; break;
        case 16:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_16; break;
        case 32:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_32; break;
        case 64:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_64; break;
        case 128:   Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_128; break;
        default: Serial.println("Error: Invalid resolution."); return;
    }
    */

    // Set the control mode to serial communication.
    Dispenser.settings.controlMode = PRODRIVER_MODE_SERIAL;

    // Initialize the dispenser driver.
    Dispenser.begin();

    // Set the current limit for the motor driver (e.g., 256 mA).
    Dispenser.setCurrentLimit(256);

    // Disable the dispenser to ensure it's off by default.
    Dispenser.disable();
}

/**
 * Enables the dispenser, allowing it to perform operations.
 * - Updates the `dispenserEnabled` flag to `true`.
 */
void DispenserControls::enableDispenser() {
    Dispenser.enable();         // Activate the dispenser driver.
    dispenserEnabled = true;    // Update the enabled state.
}

/**
 * Disables the dispenser, preventing it from operating.
 * - Updates the `dispenserEnabled` flag to `false`.
 */
void DispenserControls::disableDispenser() {
    Dispenser.disable();        // Deactivate the dispenser driver.
    dispenserEnabled = false;   // Update the enabled state.
}

/**
 * Checks whether the dispenser is currently enabled.
 * 
 * Returns:
 * - `true` if the dispenser is enabled, `false` otherwise.
 */
bool DispenserControls::isDispenserEnabled() {
    return dispenserEnabled;
}

/**
 * Changes the dispensing direction.
 * 
 * Parameters:
 * - `dir` (int): Direction for the dispenser (0 for one direction, 1 for the opposite).
 * 
 * Behavior:
 * - Updates the `dispenseDir` variable if the direction is valid (0 or 1).
 * - Prints an error message and disables the dispenser if an invalid direction is provided.
 */
void DispenserControls::changeDir(int dir) {
    if (dir == 0 || dir == 1) {
        dispenseDir = dir;  // Update the dispensing direction.
    } else {
        Serial.println("Error: Invalid direction.");  // Print error message.
        disableDispenser();                           // Disable the dispenser.
        while (1);                                    // Halt execution.
    }
}

/**
 * Performs a dispensing operation by moving the stepper motor.
 * 
 * Parameters:
 * - `steps` (int): Number of steps to move the motor.
 * - `dir` (int): Direction to move the motor (0 or 1).
 * 
 * Behavior:
 * - Sends a command to the dispenser to perform the specified number of steps in the given direction.
 */
void DispenserControls::dispense(int steps, int dir) {
    Dispenser.stepSerial(steps, dir);  // Command the dispenser to step.
}
