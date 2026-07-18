/**
 * @file mag_phase.c
 * @brief Legacy amplitude helpers for the I/Q phase module.
 */

#include "mag_phase.h"
#include <math.h>
#include <stddef.h>

// RMS-based amplitude helpers for sine, square, and triangle inputs.

float Measuring_Sine_Amplitude(uint16_t length,uint16_t *AD_value)
{
	uint32_t i;
	double sum = 0.0;
	double mean;
	double square_sum = 0.0;
	const double scale = 3.3 / 4096.0;

	if (AD_value == NULL || length == 0U) {
		return 0.0f;
	}
	for (i = 0U; i < (uint32_t)length; ++i) {
		sum += AD_value[i];
	}
	mean = sum / (double)length;
	for (i = 0U; i < (uint32_t)length; ++i) {
		const double difference = ((double)AD_value[i] - mean) * scale;
		square_sum += difference * difference;
	}
	return sqrtf((float)(2.0 * square_sum / (double)length));
}

float Measuring_Square_Amplitude(uint16_t length,uint16_t *AD_value)
{
	uint32_t i;
	double sum = 0.0;
	double mean;
	double square_sum = 0.0;
	const double scale = 3.3 / 4096.0;

	if (AD_value == NULL || length == 0U) {
		return 0.0f;
	}
	for (i = 0U; i < (uint32_t)length; ++i) {
		sum += AD_value[i];
	}
	mean = sum / (double)length;
	for (i = 0U; i < (uint32_t)length; ++i) {
		const double difference = ((double)AD_value[i] - mean) * scale;
		square_sum += difference * difference;
	}
	return sqrtf((float)(square_sum / (double)length));
}

float Measuring_Triangle_Amplitude(uint16_t length,uint16_t *AD_value)
{
	uint32_t i;
	double sum = 0.0;
	double mean;
	double square_sum = 0.0;
	const double scale = 3.3 / 4096.0;

	if (AD_value == NULL || length == 0U) {
		return 0.0f;
	}
	for (i = 0U; i < (uint32_t)length; ++i) {
		sum += AD_value[i];
	}
	mean = sum / (double)length;
	for (i = 0U; i < (uint32_t)length; ++i) {
		const double difference = ((double)AD_value[i] - mean) * scale;
		square_sum += difference * difference;
	}
	return sqrtf((float)(3.0 * square_sum / (double)length));
}

