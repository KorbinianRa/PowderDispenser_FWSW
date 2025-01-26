#include "MixerControls.h"

/**
 * Constructor for the MixerControls class.
 * 
 * Initializes the utility class and assigns default relay addresses for the mixer and drain.
 * Parameters:
 * - `utils` (Utils&): Reference to the utility class for shared functionality.
 */
MixerControls::MixerControls(Utils& utils) 
    : utils(utils), relay_mixer(RELAY_ADDR2), relay_drain(RELAY_ADDR1) {
    // Constructor body (no additional initialization required here)
}

/**
 * Initializes a Qwiic relay at its assigned address.
 * 
 * Parameters:
 * - `relay` (Qwiic_Relay&): The relay object to initialize.
 * 
 * Behavior:
 * - Attempts to connect to the relay.
 * - Prints a message indicating whether the connection was successful or failed.
 */
void MixerControls::setupRelay(Qwiic_Relay &relay) {
    if (!relay.begin()) {
        Serial.println("Can't communicate with relay at the current address. Trying suggested address...");
    } else {
        Serial.println("Relay connected at the current address!");
    }
}

/**
 * Checks the current state of a relay (on/off).
 * 
 * Parameters:
 * - `relay` (Qwiic_Relay&): The relay object to query.
 * 
 * Returns:
 * - `true` if the relay is on, `false` otherwise.
 */
bool MixerControls::checkRelayState(Qwiic_Relay &relay) {
    bool state = relay.getState();  // Query the state of the relay.
    return state;
}

/**
 * Runs a relay for a specified duration.
 * 
 * Parameters:
 * - `relay` (Qwiic_Relay&): The relay to control.
 * - `runTime` (float): Duration to run the relay, in seconds.
 * 
 * Behavior:
 * - Turns the relay on.
 * - Waits for the specified duration.
 * - Turns the relay off.
 */
void MixerControls::run(Qwiic_Relay &relay, float runTime) {
    relay.turnRelayOn();                 // Activate the relay.
    delay(runTime * 1000);               // Wait for the specified time in milliseconds.
    relay.turnRelayOff();                // Deactivate the relay.
}

/**
 * Sets up a digital output pin for controlling a relay.
 * 
 * Parameters:
 * - `pin` (uint8_t): The pin number connected to the relay.
 * 
 * Behavior:
 * - Configures the pin as an output.
 * - Ensures the relay is initially off by setting the pin to LOW.
 */
void MixerControls::setupPump(uint8_t pin) {
    pinMode(pin, OUTPUT);       // Set the pin as an output.
    digitalWrite(pin, LOW);     // Ensure the relay is off initially.
}

/**
 * Runs a pump relay connected to a specific pin for a specified duration.
 * 
 * Parameters:
 * - `pin` (uint8_t): The pin number connected to the pump relay.
 * - `runTime` (float): Duration to run the pump, in seconds.
 * 
 * Behavior:
 * - Sets the pin HIGH to activate the pump.
 * - Waits for the specified duration.
 * - Sets the pin LOW to deactivate the pump.
 */
void MixerControls::runPump(uint8_t pin, float runTime) {
    digitalWrite(pin, HIGH);    // Turn the pump on.
    delay(runTime * 1000);      // Wait for the specified duration in milliseconds.
    digitalWrite(pin, LOW);     // Turn the pump off.
}
