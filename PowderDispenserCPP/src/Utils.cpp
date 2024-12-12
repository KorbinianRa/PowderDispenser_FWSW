<<<<<<< HEAD
#include "Utils.h"

Utils::Utils() {}

void Utils::setupArduino() {
    Serial.begin(115200);
    delay(500);
    Wire.begin();
}

void Utils::clearEEPROM() {
    for (int i = 0; i < EEPROM.length(); i++) {
        EEPROM.write(i, 0);
    }
=======
#include "Utils.h"

Utils::Utils() {}

void Utils::setupArduino() {
    Serial.begin(115200);
    delay(500);
    Wire.begin();
}

void Utils::clearEEPROM() {
    for (int i = 0; i < EEPROM.length(); i++) {
        EEPROM.write(i, 0);
    }
>>>>>>> c5e728c45412297ccfbd7313ba623480bfd3dee3
}