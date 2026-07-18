#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#include "benchmark.h"
#include "mag_phase.h"
#include "signal_data.h"

#if SIGNAL_LENGTH != 4096
#error "test_mag_phase requires SIGNAL_LENGTH == 4096"
#endif

#define MAG_PHASE_BENCHMARK_ITERATIONS 1000U

static uint16_t guarded[SIGNAL_LENGTH + 1U];
static uint16_t zero_guarded[SIGNAL_LENGTH + 1U];

typedef float (*amplitude_function_t)(uint16_t length, uint16_t *samples);

static int check_guard_invariance(const char *label, amplitude_function_t measure)
{
    const uint16_t length = (uint16_t)SIGNAL_LENGTH;
    const float with_zero_guard = measure(length, zero_guarded);
    const float with_max_guard = measure(length, guarded);
    const float difference = fabsf(with_max_guard - with_zero_guard);

    fprintf(stderr, "GUARD:%s:%.9f\n", label, difference);
    return isfinite(difference) && difference <= 1.0e-6f ? 0 : 5;
}

static int check_invalid_inputs(const char *label, amplitude_function_t measure)
{
    const float empty_result = measure(0U, guarded);
    const float null_result = measure(1U, NULL);

    fprintf(stderr, "INVALID:%s:%.1f:%.1f\n", label, empty_result, null_result);
    return empty_result == 0.0f && null_result == 0.0f ? 0 : 6;
}

static int print_benchmark(const char *label, clock_t begin, clock_t end)
{
    const double average_us = benchmark_average_us(
        begin, end, MAG_PHASE_BENCHMARK_ITERATIONS);

    printf("BENCH:%s:%u:%.6f\n", label, MAG_PHASE_BENCHMARK_ITERATIONS,
           average_us);
    return isfinite(average_us) && average_us > 0.0 ? 0 : 4;
}

int main(void)
{
    const uint16_t length = (uint16_t)SIGNAL_LENGTH;
    clock_t begin;
    clock_t end;
    float sine;
    float square;
    float triangle;
    volatile float benchmark_sink = 0.0f;
    unsigned int iteration;
    int guard_status;
    int invalid_status;

    memcpy(guarded, test_signal_raw, sizeof(test_signal_raw));
    guarded[SIGNAL_LENGTH] = 4095U;
    memcpy(zero_guarded, test_signal_raw, sizeof(test_signal_raw));
    zero_guarded[SIGNAL_LENGTH] = 0U;

    sine = Measuring_Sine_Amplitude(length, guarded);
    square = Measuring_Square_Amplitude(length, guarded);
    triangle = Measuring_Triangle_Amplitude(length, guarded);
    printf("RESULT:mag_phase_sine:%.6f\n", sine);
    printf("RESULT:mag_phase_square:%.6f\n", square);
    printf("RESULT:mag_phase_triangle:%.6f\n", triangle);

    guard_status = check_guard_invariance("mag_phase_sine", Measuring_Sine_Amplitude);
    guard_status |= check_guard_invariance("mag_phase_square", Measuring_Square_Amplitude);
    guard_status |= check_guard_invariance("mag_phase_triangle", Measuring_Triangle_Amplitude);
    if (guard_status != 0) {
        return 5;
    }

    invalid_status = check_invalid_inputs("mag_phase_sine", Measuring_Sine_Amplitude);
    invalid_status |= check_invalid_inputs("mag_phase_square", Measuring_Square_Amplitude);
    invalid_status |= check_invalid_inputs("mag_phase_triangle", Measuring_Triangle_Amplitude);
    if (invalid_status != 0) {
        return 6;
    }

    benchmark_sink += Measuring_Sine_Amplitude(length, guarded);
    begin = clock();
    for (iteration = 0U; iteration < MAG_PHASE_BENCHMARK_ITERATIONS; ++iteration) {
        benchmark_sink += Measuring_Sine_Amplitude(length, guarded);
    }
    end = clock();
    if (print_benchmark("mag_phase_sine", begin, end) != 0) {
        return 4;
    }

    benchmark_sink += Measuring_Square_Amplitude(length, guarded);
    begin = clock();
    for (iteration = 0U; iteration < MAG_PHASE_BENCHMARK_ITERATIONS; ++iteration) {
        benchmark_sink += Measuring_Square_Amplitude(length, guarded);
    }
    end = clock();
    if (print_benchmark("mag_phase_square", begin, end) != 0) {
        return 4;
    }

    benchmark_sink += Measuring_Triangle_Amplitude(length, guarded);
    begin = clock();
    for (iteration = 0U; iteration < MAG_PHASE_BENCHMARK_ITERATIONS; ++iteration) {
        benchmark_sink += Measuring_Triangle_Amplitude(length, guarded);
    }
    end = clock();
    if (print_benchmark("mag_phase_triangle", begin, end) != 0) {
        return 4;
    }

    return benchmark_sink == -1.0f ? 3 : 0;
}
