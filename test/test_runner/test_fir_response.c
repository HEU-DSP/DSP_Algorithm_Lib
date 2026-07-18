/**
 * @file test_fir_response.c
 * @brief Validate the fixed FIR wrapper against the generated convolution reference.
 */

#include <math.h>
#include <stdio.h>
#include <time.h>

#include "benchmark.h"
#include "fir_filter.h"
#include "signal_data.h"

#define FIR_BENCH_ITERATIONS 200U

#if SIGNAL_LENGTH != NUM_PER_CALL
#error "FIR response validation requires exactly NUM_PER_CALL samples"
#endif

int main(void)
{
    float32_t output[SIGNAL_LENGTH];
    float32_t benchmark_output[SIGNAL_LENGTH];
    volatile float32_t sink = 0.0f;

    arm_emg_f32_filter_init();
    arm_emg_f32_filter(test_signal_float, output);

    float32_t max_abs_error = 0.0f;
    for (unsigned int index = 0; index < SIGNAL_LENGTH; ++index) {
        const float32_t error = fabsf(output[index] - expected_fir_output[index]);
        if (error > max_abs_error) {
            max_abs_error = error;
        }
    }
    printf("RESULT:fir_max_abs_error:%.9g\n", (double)max_abs_error);

    arm_emg_f32_filter_init();
    arm_emg_f32_filter(test_signal_float, benchmark_output);
    sink += benchmark_output[SIGNAL_LENGTH - 1U];

    arm_emg_f32_filter_init();
    const clock_t begin = clock();
    for (unsigned int iteration = 0; iteration < FIR_BENCH_ITERATIONS; ++iteration) {
        arm_emg_f32_filter(test_signal_float, benchmark_output);
        sink += benchmark_output[iteration % SIGNAL_LENGTH];
    }
    const clock_t end = clock();
    const double average_us = benchmark_average_us(
        begin, end, FIR_BENCH_ITERATIONS
    );

    printf("BENCH:fir_filter:%u:%.9g\n", FIR_BENCH_ITERATIONS, average_us);
    return (!isfinite(average_us) || average_us <= 0.0 || !isfinite(sink)) ? 1 : 0;
}
