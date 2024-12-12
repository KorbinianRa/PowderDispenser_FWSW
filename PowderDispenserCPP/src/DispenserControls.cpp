<<<<<<< HEAD
#include "DispenserControls.h"

bool DispenserControls::dispenserEnabled = false;

DispenserControls::DispenserControls(Utils& utils) : utils(utils) {}

void DispenserControls::setupDispenser(int resVar) {
    // switch (resVar) {
    //     case 2:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_2; break;
    //     case 4:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_4; break;
    //     case 8:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_8; break;
    //     case 16:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_16; break;
    //     case 32:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_32; break;
    //     case 64:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_64; break;
    //     case 128:   Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_128; break;
    //     default: Serial.println("Error: Invalid resolution."); return;
    // }
    Dispenser.settings.controlMode = PRODRIVER_MODE_SERIAL;
    Dispenser.begin();
    Dispenser.setCurrentLimit(256);
    Dispenser.disable();
}

void DispenserControls::enableDispenser() {
    Dispenser.enable();
    dispenserEnabled = true;
}

void DispenserControls::disableDispenser() {
    Dispenser.disable();
    dispenserEnabled = false;
}

bool DispenserControls::isDispenserEnabled() {
    return dispenserEnabled;
}

void DispenserControls::changeDir(int dir) {
    if (dir == 0 || dir == 1) {
        dispenseDir = dir;
    } else {
        Serial.println("Error: Invalid direction.");
        disableDispenser();
        while (1);
    }
}

void DispenserControls::dispense(int steps, int dir) {
    Dispenser.stepSerial(steps, dir);
}
=======
#include "DispenserControls.h"

bool DispenserControls::dispenserEnabled = false;

DispenserControls::DispenserControls(Utils& utils) : utils(utils) {}

void DispenserControls::setupDispenser(int resVar) {
    // switch (resVar) {
    //     case 2:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_2; break;
    //     case 4:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_4; break;
    //     case 8:     Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_8; break;
    //     case 16:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_16; break;
    //     case 32:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_32; break;
    //     case 64:    Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_64; break;
    //     case 128:   Dispenser.settings.stepResolutionMode = PRODRIVER_STEP_RESOLUTION_VARIABLE_1_128; break;
    //     default: Serial.println("Error: Invalid resolution."); return;
    // }
    Dispenser.settings.controlMode = PRODRIVER_MODE_SERIAL;
    Dispenser.begin();
    Dispenser.setCurrentLimit(256);
    Dispenser.disable();
}

void DispenserControls::enableDispenser() {
    Dispenser.enable();
    dispenserEnabled = true;
}

void DispenserControls::disableDispenser() {
    Dispenser.disable();
    dispenserEnabled = false;
}

bool DispenserControls::isDispenserEnabled() {
    return dispenserEnabled;
}

void DispenserControls::changeDir(int dir) {
    if (dir == 0 || dir == 1) {
        dispenseDir = dir;
    } else {
        Serial.println("Error: Invalid direction.");
        disableDispenser();
        while (1);
    }
}

void DispenserControls::dispense(int steps, int dir) {
    Dispenser.stepSerial(steps, dir);
}
>>>>>>> c5e728c45412297ccfbd7313ba623480bfd3dee3
