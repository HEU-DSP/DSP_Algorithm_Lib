/**
 * @file mag_phase.c
 * @brief I/Q 测相模块附带的旧版幅度测量辅助函数。
 */

#include "mag_phase.h"
#include <math.h>
#include <stddef.h>

/* 分别针对正弦波、方波和三角波的有效值测幅辅助函数。
 * 正弦波波形系数 A=2，峰值 = sqrt(2) × RMS。
 * 方波波形系数 A=1，峰值 = RMS。
 * 三角波波形系数 A=3，峰值 = sqrt(3) × RMS。 */

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
