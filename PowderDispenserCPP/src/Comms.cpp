<<<<<<< HEAD
#include "Comms.h"

char Comms::inputBuffer[Comms::buffSize] = {0};
unsigned long Comms::curMillis = 0;
unsigned long Comms::prevReplyToPCmillis = 0;
unsigned long Comms::replyToPCinterval = 1000;

Comms::Comms(Utils& utils, ScaleControls& scaleControls, MixerControls& mixerControls, DispenserControls& dispenserControls)
    : utils(utils), scaleControls(scaleControls), mixerControls(mixerControls), dispenserControls(dispenserControls) {}

void Comms::getDataFromPC() {
    while (Serial.available() > 0) {
        char x = Serial.read();
        if (bytesRecvd < buffSize - 1) {
            if (x == endMarker) {
                readInProgress = false;
                newDataFromPC = true;
                inputBuffer[bytesRecvd] = 0;
                parseData();
            } else if (readInProgress) {
                inputBuffer[bytesRecvd++] = x;
            } else if (x == startMarker) { 
                bytesRecvd = 0; 
                readInProgress = true;
            }
        } else {
            bytesRecvd = buffSize - 1;
        }
    }
}

void Comms::replyToPC() {
    if (newDataFromPC) {
        newDataFromPC = false;
        Serial.print("<Msg ");
        Serial.print(messageFromPC);
        Serial.print(" Time ");
        Serial.print(curMillis >> 9);
        Serial.println(">");
    }
}


void Comms::parseData() {
    strcpy(messageFromPC, inputBuffer);
    char *token = strtok(inputBuffer, ",");
    
    if (strcmp(token, "Mix") == 0) {
        float duration = atof(strtok(NULL, ","));
        mixerControls.run(mixerControls.getMixerRelay(), duration);
        replyToPC();
    } else if (strcmp(token, "Drain") == 0) {
        float duration = atof(strtok(NULL, ","));
        mixerControls.run(mixerControls.getDrainRelay(), duration);
        replyToPC();
    } else if (strcmp(token, "Pump") == 0) {
        int pin = atoi(strtok(NULL, ","));
        float duration = atof(strtok(NULL, ","));
        mixerControls.runPump(pin, duration);
        replyToPC();
    } else if (strcmp(token, "Dispense") == 0) {
        int steps = atoi(strtok(NULL, ","));
        int dir = atoi(strtok(NULL, ","));
        dispenserControls.dispense(steps, dir);
        replyToPC();
    } else if (strcmp(token, "DispenserOn") == 0) {
        dispenserControls.enableDispenser();
        replyToPC();
    } else if (strcmp(token, "DispenserOff") == 0) {
        dispenserControls.disableDispenser();
        replyToPC();
    } else if (strcmp(token, "ScaleOn") == 0) {
        scaleControls.scaleOn();
        replyToPC();
    } else if (strcmp(token, "ScaleOff") == 0) {
        scaleControls.scaleOff();
        replyToPC();
    } else if (strcmp(token, "Meas") == 0) {
        replyToPC();
        uint8_t avgReadingSamples = atoi(strtok(NULL, ","));
        FilterType filterType = scaleControls.getFilterTypeFromString(strtok(NULL, ","));
        scaleControls.sendWeight(avgReadingSamples, filterType);
    } else if (strcmp(token, "ADC") == 0) {
        replyToPC();
        uint8_t avgReadingSamples = atoi(strtok(NULL, ","));
        FilterType filterType = scaleControls.getFilterTypeFromString(strtok(NULL, ","));
        scaleControls.sendRaw(avgReadingSamples, filterType);
    } else if (strcmp(token, "Tare") == 0) {
        scaleControls.tareScale();
        replyToPC();
    } else {
        replyToPC();
    }
}
=======
#include "Comms.h"

char Comms::inputBuffer[Comms::buffSize] = {0};
unsigned long Comms::curMillis = 0;
unsigned long Comms::prevReplyToPCmillis = 0;
unsigned long Comms::replyToPCinterval = 1000;

Comms::Comms(Utils& utils, ScaleControls& scaleControls, MixerControls& mixerControls, DispenserControls& dispenserControls)
    : utils(utils), scaleControls(scaleControls), mixerControls(mixerControls), dispenserControls(dispenserControls) {}

void Comms::getDataFromPC() {
    while (Serial.available() > 0) {
        char x = Serial.read();
        if (bytesRecvd < buffSize - 1) {
            if (x == endMarker) {
                readInProgress = false;
                newDataFromPC = true;
                inputBuffer[bytesRecvd] = 0;
                parseData();
            } else if (readInProgress) {
                inputBuffer[bytesRecvd++] = x;
            } else if (x == startMarker) { 
                bytesRecvd = 0; 
                readInProgress = true;
            }
        } else {
            bytesRecvd = buffSize - 1;
        }
    }
}

void Comms::replyToPC() {
    if (newDataFromPC) {
        newDataFromPC = false;
        Serial.print("<Msg ");
        Serial.print(messageFromPC);
        Serial.print(" Time ");
        Serial.print(curMillis >> 9);
        Serial.println(">");
    }
}


void Comms::parseData() {
    strcpy(messageFromPC, inputBuffer);
    char *token = strtok(inputBuffer, ",");
    
    if (strcmp(token, "Mix") == 0) {
        float duration = atof(strtok(NULL, ","));
        mixerControls.run(mixerControls.getMixerRelay(), duration);
        replyToPC();
    } else if (strcmp(token, "Drain") == 0) {
        float duration = atof(strtok(NULL, ","));
        mixerControls.run(mixerControls.getDrainRelay(), duration);
        replyToPC();
    } else if (strcmp(token, "Pump") == 0) {
        int pin = atoi(strtok(NULL, ","));
        float duration = atof(strtok(NULL, ","));
        mixerControls.runPump(pin, duration);
        replyToPC();
    } else if (strcmp(token, "Dispense") == 0) {
        int steps = atoi(strtok(NULL, ","));
        int dir = atoi(strtok(NULL, ","));
        dispenserControls.dispense(steps, dir);
        replyToPC();
    } else if (strcmp(token, "DispenserOn") == 0) {
        dispenserControls.enableDispenser();
        replyToPC();
    } else if (strcmp(token, "DispenserOff") == 0) {
        dispenserControls.disableDispenser();
        replyToPC();
    } else if (strcmp(token, "ScaleOn") == 0) {
        scaleControls.scaleOn();
        replyToPC();
    } else if (strcmp(token, "ScaleOff") == 0) {
        scaleControls.scaleOff();
        replyToPC();
    } else if (strcmp(token, "Meas") == 0) {
        replyToPC();
        uint8_t avgReadingSamples = atoi(strtok(NULL, ","));
        FilterType filterType = scaleControls.getFilterTypeFromString(strtok(NULL, ","));
        scaleControls.sendWeight(avgReadingSamples, filterType);
    } else if (strcmp(token, "ADC") == 0) {
        replyToPC();
        uint8_t avgReadingSamples = atoi(strtok(NULL, ","));
        FilterType filterType = scaleControls.getFilterTypeFromString(strtok(NULL, ","));
        scaleControls.sendRaw(avgReadingSamples, filterType);
    } else if (strcmp(token, "Tare") == 0) {
        scaleControls.tareScale();
        replyToPC();
    } else {
        replyToPC();
    }
}
>>>>>>> c5e728c45412297ccfbd7313ba623480bfd3dee3
