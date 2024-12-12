#ifndef COMMS_H
#define COMMS_H

#include "Utils.h"
#include "ScaleControls.h"
#include "MixerControls.h"
#include "DispenserControls.h"

class Comms {
private:
    Utils& utils;
    ScaleControls& scaleControls;
    MixerControls& mixerControls;
    DispenserControls& dispenserControls;

    static const byte buffSize = 128;
    static char inputBuffer[buffSize];
    const char startMarker = '<';
    const char endMarker = '>';
    byte bytesRecvd = 0;
    bool readInProgress = false;
    bool newDataFromPC = false;

    char messageFromPC[buffSize] = {0};

    static unsigned long prevReplyToPCmillis;
    static unsigned long replyToPCinterval;
    
    void parseData();
    void replyToPC();

public:
    Comms(Utils& utils, ScaleControls& scaleControls, MixerControls& mixerControls, DispenserControls& dispenserControls);

    void getDataFromPC();
    static inline void updateCurMillis(unsigned long millis) { curMillis = millis; }

private:
    static unsigned long curMillis;
};

#endif // COMMS_H
