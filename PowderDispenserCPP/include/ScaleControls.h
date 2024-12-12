<<<<<<< HEAD
#ifndef SCALECONTROLS_H
#define SCALECONTROLS_H

#include "Utils.h"
#include <SparkFun_Qwiic_Scale_NAU7802_Arduino_Library.h>
#include <Ewma.h>

enum FilterType {
    NONE,
    EWMA,
    SMA,
    LPF
};

class ScaleControls {
public:
    ScaleControls(Utils& utils);

    void setupScale(int sampleRate = 320, int gain = 128, int ldoVoltage = 3);
    void scaleOn();
    void scaleOff();
    float getReading(uint8_t avgReadingSamples = 100, FilterType filterType = EWMA, unsigned long timeout_ms = 1000);
    float convertToWeight(float reading);
    void sendWeight(uint8_t avgReadingSamples = 100, FilterType filterType = EWMA, unsigned long timeout_ms = 1000);
    void sendRaw(uint8_t avgReadingSamples = 100, FilterType filterType = EWMA, unsigned long timeout_ms = 1000);
    static FilterType getFilterTypeFromString(const char* filterTypeStr);
    void calculateCalParams(float manual_slope, float manual_intercept);
    float applyFilter(float reading, FilterType filterType = EWMA);
    void tareScale();

    static constexpr bool allowNegative = true;
    static constexpr uint8_t numReadings = 10;
    static const uint8_t numMeas;
    static const float MANUAL_SLOPE;
    static const float MANUAL_INTERCEPT;
    static const float lpfAlpha;
    static float smaFilterValues[numReadings];

    static const int LOC_CALIBRATION_FACTOR;
    static const int LOC_ZERO_OFFSET;
    static const int LOC_CH1_OFFSET;

private:
    Utils& utils;
    NAU7802 Scale;
    Ewma ewmaFilter;

    float lpfFilterValue;
    bool settingsDetected;
    bool scaleRunning;
};

#endif // SCALECONTROLS_H
=======
#ifndef SCALECONTROLS_H
#define SCALECONTROLS_H

#include "Utils.h"
#include <SparkFun_Qwiic_Scale_NAU7802_Arduino_Library.h>
#include <Ewma.h>

enum FilterType {
    NONE,
    EWMA,
    SMA,
    LPF
};

class ScaleControls {
public:
    ScaleControls(Utils& utils);

    void setupScale(int sampleRate = 320, int gain = 128, int ldoVoltage = 3);
    void scaleOn();
    void scaleOff();
    float getReading(uint8_t avgReadingSamples = 100, FilterType filterType = EWMA, unsigned long timeout_ms = 1000);
    float convertToWeight(float reading);
    void sendWeight(uint8_t avgReadingSamples = 100, FilterType filterType = EWMA, unsigned long timeout_ms = 1000);
    void sendRaw(uint8_t avgReadingSamples = 100, FilterType filterType = EWMA, unsigned long timeout_ms = 1000);
    static FilterType getFilterTypeFromString(const char* filterTypeStr);
    void calculateCalParams(float manual_slope, float manual_intercept);
    float applyFilter(float reading, FilterType filterType = EWMA);
    void tareScale();

    static constexpr bool allowNegative = true;
    static constexpr uint8_t numReadings = 10;
    static const uint8_t numMeas;
    static const float MANUAL_SLOPE;
    static const float MANUAL_INTERCEPT;
    static const float lpfAlpha;
    static float smaFilterValues[numReadings];

    static const int LOC_CALIBRATION_FACTOR;
    static const int LOC_ZERO_OFFSET;
    static const int LOC_CH1_OFFSET;

private:
    Utils& utils;
    NAU7802 Scale;
    Ewma ewmaFilter;

    float lpfFilterValue;
    bool settingsDetected;
    bool scaleRunning;
};

#endif // SCALECONTROLS_H
>>>>>>> c5e728c45412297ccfbd7313ba623480bfd3dee3
