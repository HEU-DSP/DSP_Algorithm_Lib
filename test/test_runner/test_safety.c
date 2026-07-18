/**
 * @file test_safety.c
 * @brief Runtime safety regression checks for fixed-size DSP wrappers.
 */

#include <math.h>
#include <stdio.h>

#include "fft_buffer.h"
#include "fir_filter.h"
#include "iq_phase.h"

int main(void)
{
    float32_t iq_input[SAMPLE_N] = {0.0f};
    float32_t iq_output[SAMPLE_N];
    const float32_t sentinel = 12345.0f;

    for (int i = 0; i < SAMPLE_N; ++i) {
        iq_output[i] = sentinel;
    }
    CalXiebo(iq_input, iq_output, SAMPLE_N - 1);

    int invalid_length_unchanged = 1;
    for (int i = 0; i < SAMPLE_N; ++i) {
        if (iq_output[i] != sentinel) {
            invalid_length_unchanged = 0;
            break;
        }
    }
    printf("RESULT:iq_invalid_length_unchanged:%d\n",
           invalid_length_unchanged);

    float32_t fir_input[NUM_PER_CALL] = {0.0f};
    float32_t fir_output[NUM_PER_CALL];
    for (int i = 0; i < NUM_PER_CALL; ++i) {
        fir_output[i] = sentinel;
    }

    arm_emg_f32_filter_init();
    arm_emg_f32_filter(fir_input, fir_output);

    float32_t max_abs = 0.0f;
    for (int i = 0; i < NUM_PER_CALL; ++i) {
        const float32_t value_abs = fabsf(fir_output[i]);
        if (value_abs > max_abs) {
            max_abs = value_abs;
        }
    }
    printf("RESULT:fir_zero_max_abs:%.9f\n", max_abs);

    return 0;
}
