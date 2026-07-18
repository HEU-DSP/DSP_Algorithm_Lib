/**
 * test_frequency.c — 测频算法测试
 *
 * 被测函数：
 *   - cfft_f32_fre(fs, AD_Value, flag=1)  — FFT 二次插值测频
 *   - cfft_f32_fre(fs, AD_Value, flag=2)  — FFT 峰值测频
 *   - ZeroCross_Freq(input, n, fs)        — 过零比较测频
 *   - ZeroCross_Period(input, n, fs)      — 过零比较测周期
 */
#include <stdio.h>
#include <stdint.h>
#include <time.h>
#include "benchmark.h"
#include "arm_math.h"
#include "signal_data.h"
#include "fft_n.h"
#include "fft_interp_freq.h"
#include "zero_cross.h"

/* fft_interp_freq.c uses global s[MAX_FFT_N], declare extern. */
extern struct compx s[MAX_FFT_N];

#if SIGNAL_LENGTH != MAX_FFT_N
#error "test_frequency requires SIGNAL_LENGTH == MAX_FFT_N (8192)"
#endif

int main(void)
{
    const unsigned int benchmark_iterations = 20U;
    const unsigned int zero_cross_benchmark_iterations = 5000U;
    clock_t begin;
    clock_t end;
    volatile float benchmark_sink = 0.0f;
    unsigned int iteration;

    /* ---- Prepare float version for zero-crossing ---- */
    float32_t signal_float[SIGNAL_LENGTH];
    for (int i = 0; i < SIGNAL_LENGTH; i++) {
        signal_float[i] = test_signal_float[i];
    }

    /* ---- 1. FFT quadratic interpolation frequency (flag=1) ---- */
    float freq_interp = cfft_f32_fre(SIGNAL_FS, test_signal_raw, 1);
    printf("RESULT:fft_interp:%.6f\n", freq_interp);

    /* ---- 2. FFT peak frequency (flag=2) ---- */
    float freq_peak = cfft_f32_fre(SIGNAL_FS, test_signal_raw, 2);
    printf("RESULT:fft_peak:%.6f\n", freq_peak);

    /* ---- 3. Zero-crossing frequency ---- */
    float freq_zc = ZeroCross_Freq(signal_float, SIGNAL_LENGTH, SIGNAL_FS);
    printf("RESULT:zero_cross_freq:%.6f\n", freq_zc);

    /* ---- 4. Zero-crossing period ---- */
    float period_zc = ZeroCross_Period(signal_float, SIGNAL_LENGTH, SIGNAL_FS);
    printf("RESULT:zero_cross_period:%.6f\n", period_zc);

    /* Warm up each measured path before timing its actual algorithm call. */
    benchmark_sink += cfft_f32_fre(SIGNAL_FS, test_signal_raw, 1);
    begin = clock();
    for (iteration = 0U; iteration < benchmark_iterations; ++iteration) {
        benchmark_sink += cfft_f32_fre(SIGNAL_FS, test_signal_raw, 1);
    }
    end = clock();
    printf("BENCH:fft_interp:%u:%.6f\n", benchmark_iterations,
           benchmark_average_us(begin, end, benchmark_iterations));

    benchmark_sink += cfft_f32_fre(SIGNAL_FS, test_signal_raw, 2);
    begin = clock();
    for (iteration = 0U; iteration < benchmark_iterations; ++iteration) {
        benchmark_sink += cfft_f32_fre(SIGNAL_FS, test_signal_raw, 2);
    }
    end = clock();
    printf("BENCH:fft_peak:%u:%.6f\n", benchmark_iterations,
           benchmark_average_us(begin, end, benchmark_iterations));

    benchmark_sink += ZeroCross_Freq(signal_float, SIGNAL_LENGTH, SIGNAL_FS);
    begin = clock();
    for (iteration = 0U; iteration < zero_cross_benchmark_iterations; ++iteration) {
        benchmark_sink += ZeroCross_Freq(signal_float, SIGNAL_LENGTH, SIGNAL_FS);
    }
    end = clock();
    printf("BENCH:zero_cross_freq:%u:%.6f\n", zero_cross_benchmark_iterations,
           benchmark_average_us(begin, end, zero_cross_benchmark_iterations));

    benchmark_sink += ZeroCross_Period(signal_float, SIGNAL_LENGTH, SIGNAL_FS);
    begin = clock();
    for (iteration = 0U; iteration < zero_cross_benchmark_iterations; ++iteration) {
        benchmark_sink += ZeroCross_Period(signal_float, SIGNAL_LENGTH, SIGNAL_FS);
    }
    end = clock();
    printf("BENCH:zero_cross_period:%u:%.6f\n", zero_cross_benchmark_iterations,
           benchmark_average_us(begin, end, zero_cross_benchmark_iterations));

    if (benchmark_sink == -1.0f) {
        return 2;
    }
    return 0;
}
