/**
 * test_amplitude.c — 测幅算法测试
 *
 * 被测函数：
 *   - Measuring_Sine_Amplitude(len, raw)    — RMS 正弦波测幅
 *   - Measuring_Square_Amplitude(len, raw)  — RMS 方波测幅
 *   - Measuring_Triangle_Amplitude(len, raw)— RMS 三角波测幅
 *
 * 注意：差分三角波测幅 (Differ_Tri_Amp) 和平顶窗 FFT 测幅
 *       因依赖特定信号形状/大数组，本 runner 暂不包含，留作后续扩展。
 */
#include <stdio.h>
#include <stdint.h>
#include <math.h>
#include <time.h>
#include "arm_math.h"
#include "benchmark.h"
#include "signal_data.h"
#include "rms_amplitude.h"

#define AMPLITUDE_BENCHMARK_ITERATIONS 1000U

typedef float (*amplitude_function_t)(uint16_t length, uint16_t *samples);

static int benchmark_amplitude(const char *label, amplitude_function_t measure,
                               uint16_t length, volatile float *sink)
{
    clock_t begin;
    clock_t end;

    *sink += measure(length, test_signal_raw);
    begin = clock();
    for (unsigned int iteration = 0U;
         iteration < AMPLITUDE_BENCHMARK_ITERATIONS; ++iteration) {
        *sink += measure(length, test_signal_raw);
    }
    end = clock();

    const double average_us = benchmark_average_us(
        begin, end, AMPLITUDE_BENCHMARK_ITERATIONS);
    printf("BENCH:%s:%u:%.6f\n", label, AMPLITUDE_BENCHMARK_ITERATIONS,
           average_us);
    return isfinite(average_us) && average_us > 0.0 ? 0 : 1;
}

int main(void)
{
    uint16_t len = (uint16_t)SIGNAL_LENGTH;
    volatile float benchmark_sink = 0.0f;

    /* ---- 1. RMS sine amplitude ---- */
    float amp_sine = Measuring_Sine_Amplitude(len, test_signal_raw);
    printf("RESULT:rms_sine:%.6f\n", amp_sine);

    /* ---- 2. RMS square amplitude ---- */
    float amp_square = Measuring_Square_Amplitude(len, test_signal_raw);
    printf("RESULT:rms_square:%.6f\n", amp_square);

    /* ---- 3. RMS triangle amplitude ---- */
    float amp_tri = Measuring_Triangle_Amplitude(len, test_signal_raw);
    printf("RESULT:rms_triangle:%.6f\n", amp_tri);

    if (benchmark_amplitude("rms_sine", Measuring_Sine_Amplitude,
                            len, &benchmark_sink) != 0 ||
        benchmark_amplitude("rms_square", Measuring_Square_Amplitude,
                            len, &benchmark_sink) != 0 ||
        benchmark_amplitude("rms_triangle", Measuring_Triangle_Amplitude,
                            len, &benchmark_sink) != 0) {
        return 2;
    }

    return benchmark_sink == -1.0f ? 3 : 0;
}
