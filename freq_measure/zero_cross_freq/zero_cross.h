/**
 * @file zero_cross.h
 * @brief Rising-edge zero-crossing frequency and period measurement.
 */

#ifndef ZERO_CROSS_H
#define ZERO_CROSS_H

#include "arm_math.h"

/**
 * @brief Estimate frequency by averaging linearly interpolated crossing periods.
 * @param[in] input AC-coupled sample buffer centered around zero.
 * @param[in] n Number of samples.
 * @param[in] fs Sampling frequency in hertz.
 * @return Frequency in hertz, or 0 when fewer than two valid crossings exist.
 */
float ZeroCross_Freq(float32_t *input, int n, float fs);

/**
 * @brief Count rising-edge zero crossings in the input buffer.
 * @param[in] input Sample buffer.
 * @param[in] n Number of samples.
 * @return Number of rising-edge zero crossings.
 */
int ZeroCross_Count(float32_t *input, int n);

/**
 * @brief Estimate period by averaging all complete interpolated crossing intervals.
 * @param[in] input AC-coupled sample buffer centered around zero.
 * @param[in] n Number of samples.
 * @param[in] fs Sampling frequency in hertz.
 * @return Period in seconds, or 0 when the input or sample rate is invalid.
 */
float ZeroCross_Period(float32_t *input, int n, float fs);

#endif /* ZERO_CROSS_H */
