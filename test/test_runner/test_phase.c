/**
 * test_phase.c — 测相算法测试
 *
 * 被测函数：
 *   - CalPhase(f, fs, N, adc_float)  — IQ 正交解调相位估计
 *   - CalXiebo(input, output, n)      — 谐波分析（FFT 幅度谱）
 */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include "benchmark.h"
#include "arm_math.h"
#include "signal_data.h"
#include "iq_phase.h"
#include "fft_buffer.h"

#if SIGNAL_LENGTH != SAMPLE_N
#error "test_phase requires SIGNAL_LENGTH == SAMPLE_N (1024)"
#endif

#define PHASE_BENCHMARK_ITERATIONS 100U

int main(void)
{
    clock_t begin;
    clock_t end;
    double average_us;
    unsigned int iteration;
    volatile float32_t benchmark_sink = 0.0f;

    /* ---- 1. IQ quadrature demodulation phase ---- */
    float phase = CalPhase(SIGNAL_FREQ, SIGNAL_FS, SIGNAL_LENGTH, test_signal_float);
    printf("RESULT:iq_phase:%.6f\n", phase);

    /* Warm up before timing the actual CalPhase calls. */
    benchmark_sink += CalPhase(SIGNAL_FREQ, SIGNAL_FS, SIGNAL_LENGTH,
                               test_signal_float);
    begin = clock();
    for (iteration = 0U; iteration < PHASE_BENCHMARK_ITERATIONS; ++iteration) {
        benchmark_sink += CalPhase(SIGNAL_FREQ, SIGNAL_FS, SIGNAL_LENGTH,
                                   test_signal_float);
    }
    end = clock();
    average_us = benchmark_average_us(begin, end, PHASE_BENCHMARK_ITERATIONS);
    if (!isfinite(average_us) || average_us <= 0.0) {
        return 2;
    }
    printf("BENCH:iq_phase:%u:%.6f\n", PHASE_BENCHMARK_ITERATIONS, average_us);

    /* ---- 2. Harmonic analysis (FFT magnitude spectrum) ---- */
    float32_t xiebo_out[SIGNAL_LENGTH];
    CalXiebo(test_signal_float, xiebo_out, SIGNAL_LENGTH);
    /* Output fundamental bin magnitude */
    int bin = (int)(SIGNAL_FREQ / (SIGNAL_FS / SIGNAL_LENGTH) + 0.5f);
    if (bin >= 0 && bin < SIGNAL_LENGTH) {
        printf("RESULT:xiebo_fundamental:%.6f\n", xiebo_out[bin]);
    }

    /* Warm up before timing the actual CalXiebo calls. */
    CalXiebo(test_signal_float, xiebo_out, SIGNAL_LENGTH);
    benchmark_sink += xiebo_out[0];
    begin = clock();
    for (iteration = 0U; iteration < PHASE_BENCHMARK_ITERATIONS; ++iteration) {
        CalXiebo(test_signal_float, xiebo_out, SIGNAL_LENGTH);
        benchmark_sink += xiebo_out[0];
    }
    end = clock();
    average_us = benchmark_average_us(begin, end, PHASE_BENCHMARK_ITERATIONS);
    if (!isfinite(average_us) || average_us <= 0.0) {
        return 3;
    }
    printf("BENCH:xiebo_fundamental:%u:%.6f\n", PHASE_BENCHMARK_ITERATIONS,
           average_us);

    if (benchmark_sink == -1.0f) {
        return 4;
    }

    return 0;
}
