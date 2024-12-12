#ifndef MIXERCONTROLS_H
#define MIXERCONTROLS_H

#include "Utils.h"
#include <SparkFun_Qwiic_Relay.h>

// Define relay addresses
#define RELAY_ADDR1 0x18
#define RELAY_ADDR2 0x19

class MixerControls {
public:
    MixerControls(Utils& utils);

    void setupRelay(Qwiic_Relay &relay);
    bool checkRelayState(Qwiic_Relay &relay);
    void run(Qwiic_Relay &relay, float runTime);

    Qwiic_Relay& getMixerRelay() {return relay_mixer;}
    Qwiic_Relay& getDrainRelay() {return relay_drain;} 

    void setupPump(uint8_t pin);
    void runPump(uint8_t pin, float runTime);

private:
    Utils& utils;
    Qwiic_Relay relay_mixer;
    Qwiic_Relay relay_drain;
};

#endif // MIXERCONTROLS_H

