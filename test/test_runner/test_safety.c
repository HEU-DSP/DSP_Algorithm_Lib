/**
 * @file test_safety.c
 * @brief 固定长度 DSP 封装的运行时安全回归检查。
 */

#include <math.h>
#include <stdio.h>
#include <time.h>

#include "benchmark.h"
#include "fft_buffer.h"
#include "fir_filter.h"
#include "iq_phase.h"

#define SAFETY_BENCHMARK_ITERATIONS 100U

static int run_safety_workload(float32_t *fir_max_abs)
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
    *fir_max_abs = max_abs;
    return invalid_length_unchanged;
}

int main(void)
{
    float32_t fir_max_abs = 0.0f;
    const int invalid_length_unchanged = run_safety_workload(&fir_max_abs);
    float32_t nyquist_input[SAMPLE_N];
    for (int i = 0; i < SAMPLE_N; ++i) {
        nyquist_input[i] = (i & 1) == 0 ? 0.25f : -0.25f;
    }
    const float32_t nyquist_phase = CalPhase(
        25600.0f, 51200.0f, SAMPLE_N, nyquist_input);
    const int nyquist_rejected = nyquist_phase == 0.0f;

    printf("RESULT:iq_invalid_length_unchanged:%d\n",
           invalid_length_unchanged);
    printf("RESULT:iq_nyquist_rejected:%d\n", nyquist_rejected);
    printf("RESULT:fir_zero_max_abs:%.9f\n", fir_max_abs);

    volatile float32_t benchmark_sink = 0.0f;
    float32_t benchmark_max_abs = 0.0f;
    benchmark_sink += (float32_t)run_safety_workload(&benchmark_max_abs);
    benchmark_sink += benchmark_max_abs;

    const clock_t begin = clock();
    for (unsigned int iteration = 0U;
         iteration < SAFETY_BENCHMARK_ITERATIONS; ++iteration) {
        benchmark_sink += (float32_t)run_safety_workload(&benchmark_max_abs);
        benchmark_sink += benchmark_max_abs;
    }
    const clock_t end = clock();
    const double average_us = benchmark_average_us(
        begin, end, SAFETY_BENCHMARK_ITERATIONS);
    printf("BENCH:safety_wrappers:%u:%.6f\n",
           SAFETY_BENCHMARK_ITERATIONS, average_us);

    if (!isfinite(average_us) || average_us <= 0.0 ||
        !isfinite(benchmark_sink)) {
        return 2;
    }

    return 0;
}
