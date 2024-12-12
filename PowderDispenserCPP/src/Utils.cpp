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
}