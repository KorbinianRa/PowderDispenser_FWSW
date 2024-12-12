<<<<<<< HEAD
#include "Utils.h"
#include "MixerControls.h"
#include "Comms.h"

Utils utils;
ScaleControls scaleControls(utils);
MixerControls mixerControls(utils);
DispenserControls dispenserControls(utils);
Comms comms(utils, scaleControls, mixerControls, dispenserControls);

void setup() {
    utils.setupArduino();
    delay(200); // Allow time for Serial Monitor to open
    scaleControls.setupScale(320, 128, 3);
    delay(200);
    mixerControls.setupRelay(mixerControls.getDrainRelay());
    delay(200);
    mixerControls.setupRelay(mixerControls.getMixerRelay());
    delay(200);
    mixerControls.setupPump(12);
    delay(200);
    dispenserControls.setupDispenser(128);
    delay(200);
    Serial.println("<Ready to push powder, baby!>"); // Tell PC we are ready
    scaleControls.calculateCalParams(scaleControls.MANUAL_SLOPE, scaleControls.MANUAL_INTERCEPT);
    scaleControls.tareScale();
}

void loop() {
    comms.updateCurMillis(millis());
    comms.getDataFromPC();
    // replyToPC();
}
=======
#include "Utils.h"
#include "MixerControls.h"
#include "Comms.h"

Utils utils;
ScaleControls scaleControls(utils);
MixerControls mixerControls(utils);
DispenserControls dispenserControls(utils);
Comms comms(utils, scaleControls, mixerControls, dispenserControls);

void setup() {
    utils.setupArduino();
    delay(200); // Allow time for Serial Monitor to open
    scaleControls.setupScale(320, 128, 3);
    delay(200);
    mixerControls.setupRelay(mixerControls.getDrainRelay());
    delay(200);
    mixerControls.setupRelay(mixerControls.getMixerRelay());
    delay(200);
    mixerControls.setupPump(12);
    delay(200);
    dispenserControls.setupDispenser(128);
    delay(200);
    Serial.println("<Ready to push powder, baby!>"); // Tell PC we are ready
    scaleControls.calculateCalParams(scaleControls.MANUAL_SLOPE, scaleControls.MANUAL_INTERCEPT);
    scaleControls.tareScale();
}

void loop() {
    comms.updateCurMillis(millis());
    comms.getDataFromPC();
    // replyToPC();
}
>>>>>>> c5e728c45412297ccfbd7313ba623480bfd3dee3
