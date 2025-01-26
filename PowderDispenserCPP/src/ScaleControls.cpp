#include "ScaleControls.h"

// Definitions for static constants and variables.
const uint8_t ScaleControls::numMeas = 10;  // Default number of measurements.
const float ScaleControls::MANUAL_SLOPE = 3.06828559218341e-05;  // Default manual slope for calibration.
const float ScaleControls::MANUAL_INTERCEPT = -12.9400964147;    // Default manual intercept for calibration.
const float ScaleControls::lpfAlpha = 0.5;                      // Low-pass filter alpha value.
float ScaleControls::smaFilterValues[numReadings] = {0};         // Buffer for SMA filter values.

const int ScaleControls::LOC_CALIBRATION_FACTOR = 0;  // EEPROM location for calibration factor.
const int ScaleControls::LOC_ZERO_OFFSET = 10;        // EEPROM location for zero offset.
const int ScaleControls::LOC_CH1_OFFSET = 20;         // EEPROM location for channel 1 offset.

// Constructor for ScaleControls class.
// - Initializes utility class and sets up default values for filters and flags.
ScaleControls::ScaleControls(Utils& utils)
    : utils(utils), ewmaFilter(0.05), lpfFilterValue(0.5), settingsDetected(false), scaleRunning(false) {}

/**
 * Sets up the scale by configuring its sample rate, gain, and LDO voltage.
 * - Also performs AFE (Analog Front End) calibration and powers down the scale afterward.
 * 
 * Parameters:
 * - `sampleRate` (int): Sets the scale's sampling rate (e.g., 10, 20, 40 Hz, etc.).
 * - `gain` (int): Sets the gain factor for the scale (e.g., 1x, 2x, 4x, etc.).
 * - `ldoVoltage` (int): Configures the LDO voltage for powering the scale.
 */
void ScaleControls::setupScale(int sampleRate, int gain, int ldoVoltage) {
    if (!Scale.begin()) {
        Serial.println("Scale not detected. Please check wiring.");
        while (1);  // Halts execution if the scale is not detected.
    }

    // Configure sample rate.
    switch (sampleRate) {
        case 10:  Scale.setSampleRate(NAU7802_SPS_10); break;
        case 20:  Scale.setSampleRate(NAU7802_SPS_20); break;
        case 40:  Scale.setSampleRate(NAU7802_SPS_40); break;
        case 80:  Scale.setSampleRate(NAU7802_SPS_80); break;
        case 320: Scale.setSampleRate(NAU7802_SPS_320); break;
        default:  Serial.println("Error: Invalid sample rate."); return;
    }

    // Configure gain.
    switch (gain) {
        case 1:   Scale.setGain(NAU7802_GAIN_1); break;
        case 2:   Scale.setGain(NAU7802_GAIN_2); break;
        case 4:   Scale.setGain(NAU7802_GAIN_4); break;
        case 8:   Scale.setGain(NAU7802_GAIN_8); break;
        case 16:  Scale.setGain(NAU7802_GAIN_16); break;
        case 32:  Scale.setGain(NAU7802_GAIN_32); break;
        case 64:  Scale.setGain(NAU7802_GAIN_64); break;
        case 128: Scale.setGain(NAU7802_GAIN_128); break;
        default:  Serial.println("Error: Invalid gain."); return;
    }

    // Configure LDO voltage.
    switch (ldoVoltage) {
        case 2: Scale.setLDO(NAU7802_LDO_2V4); break;
        case 3: Scale.setLDO(NAU7802_LDO_3V0); break;
        case 4: Scale.setLDO(NAU7802_LDO_3V3); break;
        case 5: Scale.setLDO(NAU7802_LDO_3V6); break;
        case 6: Scale.setLDO(NAU7802_LDO_3V9); break;
        case 7: Scale.setLDO(NAU7802_LDO_4V2); break;
        case 8: Scale.setLDO(NAU7802_LDO_4V5); break;
        default: Serial.println("Error: Invalid LDO voltage."); return;
    }

    // Perform AFE (Analog Front End) calibration.
    Scale.calibrateAFE();

    // Mark the scale as running and power it down.
    scaleRunning = true;
    Scale.powerDown();
}

/**
 * Powers up the scale to make it operational.
 */
void ScaleControls::scaleOn() {
    Scale.powerUp();
}

/**
 * Powers down the scale to save energy when not in use.
 */
void ScaleControls::scaleOff() {
    Scale.powerDown();
}

/**
 * Calculates and sets the calibration parameters (slope and zero offset) for the scale.
 * Parameters:
 * - `manual_slope` (float): The slope derived from manual calibration.
 * - `manual_intercept` (float): The intercept derived from manual calibration.
 */
void ScaleControls::calculateCalParams(float manual_slope, float manual_intercept) {
    float calibrationFactor = 1.0 / manual_slope;  // Compute the calibration factor.
    float zeroOffset = (-manual_intercept * calibrationFactor);  // Compute zero offset.

    // Apply the computed parameters to the scale.
    Scale.setCalibrationFactor(calibrationFactor);
    Scale.setZeroOffset(zeroOffset);
}

/**
 * Applies a specified filter to a scale reading.
 * Parameters:
 * - `reading` (float): The raw scale reading.
 * - `filterType` (FilterType): The type of filter to apply (e.g., EWMA, SMA, LPF, or NONE).
 * 
 * Returns:
 * - The filtered reading (float).
 */
float ScaleControls::applyFilter(float reading, FilterType filterType) {
    float filteredReading = reading;

    switch (filterType) {
        case EWMA:  // Exponentially Weighted Moving Average filter.
            filteredReading = ewmaFilter.filter(reading);
            break;

        case SMA:  // Simple Moving Average filter.
            static int index = 0;
            static float sum = 0;
            static int count = 0;

            sum -= smaFilterValues[index];  // Subtract the oldest value from the sum.
            smaFilterValues[index] = reading;  // Add the new value to the buffer.
            sum += reading;  // Add the new value to the sum.
            index = (index + 1) % numReadings;  // Update the buffer index.
            if (count < numReadings) count++;
            filteredReading = sum / count;  // Compute the average.
            break;

        case LPF:  // Low-Pass Filter.
            filteredReading = lpfAlpha * reading + (1.0 - lpfAlpha) * lpfFilterValue;
            lpfFilterValue = filteredReading;
            break;

        case NONE:  // No filtering.
        default:
            break;
    }
    return filteredReading;
}

/**
 * Reads and averages scale readings over a specified number of samples.
 * Parameters:
 * - `avgReadingSamples` (uint8_t): Number of readings to average.
 * - `filterType` (FilterType): The type of filter to apply to each reading.
 * - `timeout_ms` (unsigned long): Maximum time allowed for the readings.
 * 
 * Returns:
 * - The averaged reading (float).
 */
float ScaleControls::getReading(uint8_t avgReadingSamples, FilterType filterType, unsigned long timeout_ms) {
    float sum = 0;
    unsigned long startTime = millis();

    for (uint8_t i = 0; i < avgReadingSamples; i++) {
        if (millis() - startTime > timeout_ms) {
            Serial.println("Timeout while averaging scale readings.");
            break;
        }

        float reading = Scale.getReading();  // Raw reading from the scale.
        float filteredReading = applyFilter(reading, filterType);  // Apply filter.
        sum += filteredReading;
    }
    return sum / avgReadingSamples;  // Return the average.
}
