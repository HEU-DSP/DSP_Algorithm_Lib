/**
 * @file rms_amplitude.c
 * @brief RMS-based waveform amplitude implementation.
 */

#include "rms_amplitude.h"

#include <math.h>
#include <stddef.h>

#define ADC_LSB_VOLTS (3.3f / 4096.0f)

static float measure_amplitude(uint16_t length,
                               const uint16_t *ad_value,
                               float shape_factor)
{
    if (length == 0U || ad_value == NULL) {
        return 0.0f;
    }

    float mean = 0.0f;
    for (uint16_t i = 0U; i < length; ++i) {
        mean += (float)ad_value[i];
    }
    mean /= (float)length;

    float sum_squares = 0.0f;
    for (uint16_t i = 0U; i < length; ++i) {
        const float centered_volts = ((float)ad_value[i] - mean) * ADC_LSB_VOLTS;
        sum_squares += centered_volts * centered_volts;
    }

    return sqrtf(shape_factor * sum_squares / (float)length);
}

float Measuring_Sine_Amplitude(uint16_t length, uint16_t *AD_value)
{
    return measure_amplitude(length, AD_value, 2.0f);
}

float Measuring_Square_Amplitude(uint16_t length, uint16_t *AD_value)
{
    return measure_amplitude(length, AD_value, 1.0f);
}

float Measuring_Triangle_Amplitude(uint16_t length, uint16_t *AD_value)
{
    return measure_amplitude(length, AD_value, 3.0f);
}
