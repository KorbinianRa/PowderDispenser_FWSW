#include "Utils.h"

/**
 * Constructor for the Utils class.
 * Used to initialize utility functions or variables (currently empty).
 */
Utils::Utils() {}

/**
 * Prepares the Arduino environment for operation.
 * - Initializes Serial communication at a baud rate of 115200.
 * - Includes a small delay to ensure the Serial interface is ready.
 * - Starts I2C (Wire library) communication for connected devices.
 */
void Utils::setupArduino() {
    Serial.begin(115200);  // Initialize Serial communication for debugging or data exchange.
    delay(500);            // Wait 500ms for Serial initialization.
    Wire.begin();          // Enable I2C communication for peripherals like sensors.
}

/**
 * Clears the entire EEPROM memory.
 * - Loops through every EEPROM address and writes a value of 0.
 * - This function can reset all stored configuration or data.
 */
void Utils::clearEEPROM() {
    for (int i = 0; i < EEPROM.length(); i++) { // Iterate over all addresses in EEPROM.
        EEPROM.write(i, 0);                     // Write 0 to clear the stored value.
    }
}