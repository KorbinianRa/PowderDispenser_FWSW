<<<<<<< HEAD
#ifndef DISPENSERCONTROLS_H
#define DISPENSERCONTROLS_H

#include "Utils.h"
#include <SparkFun_ProDriver_TC78H670FTG_Arduino_Library.h>

class DispenserControls {
public:
    DispenserControls(Utils& utils);

    void setupDispenser(int resVar);
    void enableDispenser();
    void disableDispenser();
    bool isDispenserEnabled();
    void changeDir(int dir);
    void dispense(int steps, int dir);

    static int dispenseDir;
    static bool dispenserEnabled;
    static const float dispenserCalFactor;

private:
    Utils& utils;
    PRODRIVER Dispenser;
};

=======
#ifndef DISPENSERCONTROLS_H
#define DISPENSERCONTROLS_H

#include "Utils.h"
#include <SparkFun_ProDriver_TC78H670FTG_Arduino_Library.h>

class DispenserControls {
public:
    DispenserControls(Utils& utils);

    void setupDispenser(int resVar);
    void enableDispenser();
    void disableDispenser();
    bool isDispenserEnabled();
    void changeDir(int dir);
    void dispense(int steps, int dir);

    static int dispenseDir;
    static bool dispenserEnabled;
    static const float dispenserCalFactor;

private:
    Utils& utils;
    PRODRIVER Dispenser;
};

>>>>>>> c5e728c45412297ccfbd7313ba623480bfd3dee3
#endif // DISPENSERCONTROLS_H