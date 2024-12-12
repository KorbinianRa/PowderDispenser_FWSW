<<<<<<< HEAD
#include "MixerControls.h"

MixerControls::MixerControls(Utils& utils) : utils(utils), relay_mixer(RELAY_ADDR2), relay_drain(RELAY_ADDR1) {
    // Constructor
}

void MixerControls::setupRelay(Qwiic_Relay &relay) {
    if (!relay.begin()) {
        Serial.println("Can't communicate with relay at the current address. Trying suggested address...");
    } else {
        Serial.println("Relay connected at the current address!");
    }
}

bool MixerControls::checkRelayState(Qwiic_Relay &relay) {
    bool state = relay.getState();
    return state;
}

void MixerControls::run(Qwiic_Relay &relay, float runTime) {
    relay.turnRelayOn();
    delay(runTime*1000);
    relay.turnRelayOff();
}

void MixerControls::setupPump(uint8_t pin) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);  // Ensure the relay is off initially
}

void MixerControls::runPump(uint8_t pin, float runTime) {
    digitalWrite(pin, HIGH);
    delay(runTime * 1000);
    digitalWrite(pin, LOW);
=======
#include "MixerControls.h"

MixerControls::MixerControls(Utils& utils) : utils(utils), relay_mixer(RELAY_ADDR2), relay_drain(RELAY_ADDR1) {
    // Constructor
}

void MixerControls::setupRelay(Qwiic_Relay &relay) {
    if (!relay.begin()) {
        Serial.println("Can't communicate with relay at the current address. Trying suggested address...");
    } else {
        Serial.println("Relay connected at the current address!");
    }
}

bool MixerControls::checkRelayState(Qwiic_Relay &relay) {
    bool state = relay.getState();
    return state;
}

void MixerControls::run(Qwiic_Relay &relay, float runTime) {
    relay.turnRelayOn();
    delay(runTime*1000);
    relay.turnRelayOff();
}

void MixerControls::setupPump(uint8_t pin) {
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);  // Ensure the relay is off initially
}

void MixerControls::runPump(uint8_t pin, float runTime) {
    digitalWrite(pin, HIGH);
    delay(runTime * 1000);
    digitalWrite(pin, LOW);
>>>>>>> c5e728c45412297ccfbd7313ba623480bfd3dee3
}