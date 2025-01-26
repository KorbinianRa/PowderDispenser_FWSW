#include "Utils.h"
#include "MixerControls.h"
#include "Comms.h"

// Global object initialization
Utils utils;  // Utility object for shared functionality.
ScaleControls scaleControls(utils);  // Scale control object using the utility class.
MixerControls mixerControls(utils); // Mixer control object using the utility class.
DispenserControls dispenserControls(utils); // Dispenser control object using the utility class.
Comms comms(utils, scaleControls, mixerControls, dispenserControls); // Communication object linking all controls.

/**
 * Arduino `setup()` function.
 * 
 * Initializes the system components, sets up the scale, mixer, dispenser, and communication modules,
 * and prepares the system for operation.
 */
void setup() {
    utils.setupArduino();  // Initialize Arduino Serial communication and I2C.
    delay(200);            // Short delay to allow the Serial Monitor to open.

    // Set up the scale with specific parameters (sample rate, gain, LDO voltage).
    scaleControls.setupScale(320, 128, 3);  // Sample rate: 320 Hz, Gain: 128x, LDO: 3.0V.
    delay(200);

    // Initialize relays for the mixer and drain.
    mixerControls.setupRelay(mixerControls.getDrainRelay());
    delay(200);
    mixerControls.setupRelay(mixerControls.getMixerRelay());
    delay(200);

    // Set up the pump on pin 12.
    mixerControls.setupPump(12);
    delay(200);

    // Initialize the dispenser with a resolution of 1/128 steps.
    dispenserControls.setupDispenser(128);
    delay(200);

    // Send a ready message to the PC.
    Serial.println("<Ready to push powder, baby!>");

    // Calculate calibration parameters for the scale using manual slope and intercept.
    scaleControls.calculateCalParams(scaleControls.MANUAL_SLOPE, scaleControls.MANUAL_INTERCEPT);

    // Tare the scale to zero the readings.
    scaleControls.tareScale();
}

/**
 * Arduino `loop()` function.
 * 
 * Continuously handles communication updates and processes incoming data from the PC.
 */
void loop() {
    // Update the current time for communication synchronization.
    comms.updateCurMillis(millis());

    // Check for and process any incoming data from the PC.
    comms.getDataFromPC();

    // Placeholder for replying to the PC (commented out).
    // replyToPC();
}
