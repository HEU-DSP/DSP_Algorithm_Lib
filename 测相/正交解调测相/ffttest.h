#ifndef _FFTTEST_H
#define _FFTTEST_H

#include <stdint.h>
#include "arm_math.h"

void Create_data2handle(float32_t *p);
void CalXiebo(float32_t *input, float32_t *output, int n);
float CalPhase(float f, float fs, int N, float32_t *adc_float);

#endif
