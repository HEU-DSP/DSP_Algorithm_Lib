#ifndef __ADC_BACKEND_H
#define __ADC_BACKEND_H

#include <stdint.h>
#include "arm_math.h"

/*
 * Hardware Abstraction Layer for ADC operations.
 *
 * Algorithm code includes ONLY this header.
 * Link one backend implementation per target:
 *   adc_backend_stm32f407.c   (12-bit ADC)
 *   adc_backend_stm32h732.c   (16-bit ADC)
 */

#define ADC_BUF_LEN 1024

void ADC_Backend_RawToVoltage(uint16_t *intArray, float32_t *floatArray, int size);

extern uint16_t ADC_CHANNEL_1[ADC_BUF_LEN];
extern uint16_t ADC_CHANNEL_2[ADC_BUF_LEN];

#endif
