/**
 * test_phase.c — 测相算法测试
 *
 * 被测函数：
 *   - CalPhase(f, fs, N, adc_float)  — IQ 正交解调相位估计
 *   - CalXiebo(input, output, n)      — 谐波分析（FFT 幅度谱）
 */
#include <stdio.h>
#include <stdint.h>
#include "arm_math.h"
#include "signal_data.h"
#include "iq_phase.h"
#include "fft_buffer.h"

#if SIGNAL_LENGTH != SAMPLE_N
#error "test_phase requires SIGNAL_LENGTH == SAMPLE_N (1024)"
#endif

int main(void)
{
    /* ---- 1. IQ quadrature demodulation phase ---- */
    float phase = CalPhase(SIGNAL_FREQ, SIGNAL_FS, SIGNAL_LENGTH, test_signal_float);
    printf("RESULT:iq_phase:%.6f\n", phase);

    /* ---- 2. Harmonic analysis (FFT magnitude spectrum) ---- */
    float32_t xiebo_out[SIGNAL_LENGTH];
    CalXiebo(test_signal_float, xiebo_out, SIGNAL_LENGTH);
    /* Output fundamental bin magnitude */
    int bin = (int)(SIGNAL_FREQ / (SIGNAL_FS / SIGNAL_LENGTH) + 0.5f);
    if (bin >= 0 && bin < SIGNAL_LENGTH) {
        printf("RESULT:xiebo_fundamental:%.6f\n", xiebo_out[bin]);
    }

    return 0;
}
