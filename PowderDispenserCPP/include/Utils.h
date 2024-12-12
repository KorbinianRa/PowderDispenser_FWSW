<<<<<<< HEAD
#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include <Wire.h>
#include <EEPROM.h>

class Utils {
    public:
        Utils();
        void setupArduino();
        void clearEEPROM();

        static int getDecimal() { return DECIMAL; }

    private:
        static const int DECIMAL = 4;
};

#endif // UTILS_H
=======
#ifndef UTILS_H
#define UTILS_H

#include <Arduino.h>
#include <Wire.h>
#include <EEPROM.h>

class Utils {
    public:
        Utils();
        void setupArduino();
        void clearEEPROM();

        static int getDecimal() { return DECIMAL; }

    private:
        static const int DECIMAL = 4;
};

#endif // UTILS_H
>>>>>>> c5e728c45412297ccfbd7313ba623480bfd3dee3
