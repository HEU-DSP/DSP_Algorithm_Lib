/*
 * ADC Backend — STM32F407
 *   12-bit ADC (0~4095), VREF = 3.3V
 */
#include "adc_backend.h"

#define ADC_VREF       3.3f
#define ADC_RESOLUTION 4095

uint16_t ADC_CHANNEL_1[ADC_BUF_LEN];
uint16_t ADC_CHANNEL_2[ADC_BUF_LEN];

void ADC_Backend_RawToVoltage(uint16_t *intArray, float32_t *floatArray, int size)
{
    for (int i = 0; i < size; i++)
    {
        floatArray[i] = (ADC_VREF * (float32_t)intArray[i]) / (float32_t)ADC_RESOLUTION;
    }
}
