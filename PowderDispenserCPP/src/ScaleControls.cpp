#include "ScaleControls.h"

const uint8_t ScaleControls::numMeas = 10;
const float ScaleControls::MANUAL_SLOPE = 3.06828559218341e-05;
const float ScaleControls::MANUAL_INTERCEPT = -12.9400964147;
const float ScaleControls::lpfAlpha = 0.5;
float ScaleControls::smaFilterValues[numReadings] = {0};

const int ScaleControls::LOC_CALIBRATION_FACTOR = 0;
const int ScaleControls::LOC_ZERO_OFFSET = 10;
const int ScaleControls::LOC_CH1_OFFSET = 20;

ScaleControls::ScaleControls(Utils& utils) : utils(utils), ewmaFilter(0.05), lpfFilterValue(0.5), settingsDetected(false), scaleRunning(false) {}

void ScaleControls::setupScale(int sampleRate, int gain, int ldoVoltage) {
    if (!Scale.begin()) {
        Serial.println("Scale not detected. Please check wiring.");
        while (1);
    }
    switch (sampleRate) {
        case 10:  Scale.setSampleRate(NAU7802_SPS_10); break;
        case 20:  Scale.setSampleRate(NAU7802_SPS_20); break;
        case 40:  Scale.setSampleRate(NAU7802_SPS_40); break;
        case 80:  Scale.setSampleRate(NAU7802_SPS_80); break;
        case 320: Scale.setSampleRate(NAU7802_SPS_320); break;
        default:  Serial.println("Error: Invalid sample rate."); return;
    }

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

    Scale.calibrateAFE();
    scaleRunning = true;

    Scale.powerDown();
}

void ScaleControls::scaleOn() {
    Scale.powerUp();
}

void ScaleControls::scaleOff() {
    Scale.powerDown();
}

void ScaleControls::calculateCalParams(float manual_slope, float manual_intercept) {
    float calibrationFactor = 1.0 / manual_slope;
    float zeroOffset = (-manual_intercept * calibrationFactor);

    Scale.setCalibrationFactor(calibrationFactor);
    Scale.setZeroOffset(zeroOffset);
}

float ScaleControls::applyFilter(float reading, FilterType filterType) {
    float filteredReading = reading;

    switch (filterType) {
        case EWMA:
            filteredReading = ewmaFilter.filter(reading);
            break;
        case SMA:
            static int index = 0;
            static float sum = 0;
            static int count = 0;

            sum -= smaFilterValues[index];
            smaFilterValues[index] = reading;
            sum += reading;
            index = (index + 1) % numReadings;
            if (count < numReadings) {
                count++;
            }
            filteredReading = sum / count;
            break;
        case LPF:
            filteredReading = lpfAlpha * reading + (1.0 - lpfAlpha) * lpfFilterValue;
            lpfFilterValue = filteredReading;
            break;
        case NONE:
        default:
            break;
    }
    return filteredReading;
}

float ScaleControls::getReading(uint8_t avgReadingSamples, FilterType filterType, unsigned long timeout_ms) {
    float sum = 0;
    unsigned long startTime = millis();
    
    for (uint8_t i = 0; i < avgReadingSamples; i++) {
        if (millis() - startTime > timeout_ms) {
            Serial.println("Timeout while averaging scale readings.");
            break;
        }

        float reading = Scale.getReading();  // Read raw value from the scale
        float filteredReading = applyFilter(reading, filterType);  // Apply the specified filter
        sum += filteredReading;
    }

    // Average over the number of samples
    return sum / avgReadingSamples;
}


float ScaleControls::convertToWeight(float reading) {
    return (reading - Scale.getZeroOffset()) / Scale.getCalibrationFactor();
}

void ScaleControls::sendWeight(uint8_t avgReadingSamples, FilterType filterType, unsigned long timeout_ms) {
    if (!scaleRunning) {
        Serial.println("<Scale not running>");
        return;
    }
    float weight = convertToWeight(getReading(avgReadingSamples, filterType, timeout_ms));
    Serial.print("<Weight:");
    Serial.print(weight, 4);
    Serial.print(",");
    Serial.print(avgReadingSamples);
    Serial.print(",");
    Serial.print(filterType);
    Serial.println(">");
}

void ScaleControls::sendRaw(uint8_t avgReadingSamples, FilterType filterType, unsigned long timeout_ms) {
    if (!scaleRunning) {
        Serial.println("<Scale not running>");
        return;
    }
    float adc = getReading(avgReadingSamples, filterType, timeout_ms);
    Serial.print("<ADC:");
    Serial.print(adc, 4);
    Serial.print(",");
    Serial.print(avgReadingSamples);
    Serial.print(",");
    Serial.print(filterType);
    Serial.println(">");
}


FilterType ScaleControls::getFilterTypeFromString(const char* filterTypeStr) {
    if (strcmp(filterTypeStr, "NONE") == 0) return NONE;
    if (strcmp(filterTypeStr, "EWMA") == 0) return EWMA;
    if (strcmp(filterTypeStr, "SMA") == 0) return SMA;
    if (strcmp(filterTypeStr, "LPF") == 0) return LPF;
    return EWMA;
}

void ScaleControls::tareScale() {
    int32_t newZeroOffset = getReading();
    Scale.setZeroOffset(newZeroOffset);
}

