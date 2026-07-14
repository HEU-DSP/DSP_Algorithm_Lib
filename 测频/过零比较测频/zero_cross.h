#ifndef __ZERO_CROSS_H
#define __ZERO_CROSS_H

#include <stdint.h>
#include "arm_math.h"

/*
 * Zero-crossing frequency measurement.
 *
 * Principle: detect rising-edge zero crossings, measure period by
 * linear interpolation between samples, average over multiple cycles.
 *
 * Usage:
 *   float freq = ZeroCross_Freq(adc_float, SAMPLE_N, sample_rate);
 */

/*
 * Rising-edge zero-crossing frequency measurement.
 *   input:     float32_t sample array (AC coupled, centered at 0)
 *   n:         number of samples
 *   fs:        sample rate (Hz)
 *   returns:   measured frequency (Hz), 0 if no valid crossing found
 */
float ZeroCross_Freq(float32_t *input, int n, float fs);

/*
 * Count zero crossings (rising edge) in the input array.
 *   input:     float32_t sample array
 *   n:         number of samples
 *   returns:   number of rising-edge zero crossings
 */
int ZeroCross_Count(float32_t *input, int n);

/*
 * Measure period using two consecutive rising-edge zero crossings.
 * Uses linear interpolation for sub-sample accuracy.
 *   input:     float32_t sample array
 *   n:         number of samples
 *   fs:        sample rate (Hz)
 *   returns:   period in seconds, 0 if less than 2 crossings found
 */
float ZeroCross_Period(float32_t *input, int n, float fs);

#endif
