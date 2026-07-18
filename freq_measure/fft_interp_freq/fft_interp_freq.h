/**
 * @file fft_interp_freq.h
 * @brief FFT peak and log-parabolic interpolation frequency estimator.
 */

#ifndef FFT_INTERP_FREQ_H
#define FFT_INTERP_FREQ_H

#include <stdint.h>

#include "arm_math.h"

/**
 * @brief Estimate signal frequency from a fixed 8192-sample ADC buffer.
 * @param[in] fs Sampling frequency in hertz.
 * @param[in] AD_Value ADC sample buffer.
 * @param[in] flag Nonzero enables log-parabolic peak interpolation.
 * @return Estimated frequency in hertz.
 */
float cfft_f32_fre(float32_t fs, uint16_t *AD_Value, uint8_t flag);

#endif /* FFT_INTERP_FREQ_H */
