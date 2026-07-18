/**
 * @file fir_filter.c
 * @brief Fixed-length CMSIS-DSP FIR filter wrapper implementation.
 */

#include "fir_filter.h"

static float32_t firStateF32[NUM_PER_CALL + FIR_EFFICIENT_NUM - 1];
static arm_fir_instance_f32 S_BP;
const float32_t firCoeffs32BP[FIR_EFFICIENT_NUM] =  // Fixed FIR coefficients supplied to CMSIS-DSP.
{
    -79954467,   180870058,   486593190,  -786079082,  -406638723,  1394848222,
    -406638723,  -786079082,   486593190,   180870058,   -79954467
};



#define DC_AFTER_FILTER     3088

// Initialize the CMSIS-DSP FIR state and coefficient binding.
void arm_emg_f32_filter_init(void)
{
    // Preserve the configured tap count and block length.
    arm_fir_init_f32(&S_BP, FIR_EFFICIENT_NUM, (float32_t *)&firCoeffs32BP[0], &firStateF32[0], NUM_PER_CALL);

}

// Filter one NUM_PER_CALL-sample input block.
void arm_emg_f32_filter(float32_t *dataInput, float32_t *dataOutput)
{
    arm_fir_f32(&S_BP, dataInput, dataOutput, NUM_PER_CALL);
}
