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

    return 0;
}
