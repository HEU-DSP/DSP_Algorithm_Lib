#ifndef __IIR_H
#define __IIR_H
#include "arm_math.h"

#define NUM_PER_CALL                1024

#define FIR_EFFICIENT_NUM           101
void arm_emg_f32_filter_init();
void arm_emg_f32_filter(float32_t *dataInput, float32_t *dataOutput);

#endif
