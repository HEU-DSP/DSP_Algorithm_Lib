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
#include "arm_math.h"
#include "signal_data.h"
#include "rms_amplitude.h"

int main(void)
{
    uint16_t len = (uint16_t)SIGNAL_LENGTH;

    /* ---- 1. RMS sine amplitude ---- */
    float amp_sine = Measuring_Sine_Amplitude(len, test_signal_raw);
    printf("RESULT:rms_sine:%.6f\n", amp_sine);

    /* ---- 2. RMS square amplitude ---- */
    float amp_square = Measuring_Square_Amplitude(len, test_signal_raw);
    printf("RESULT:rms_square:%.6f\n", amp_square);

    /* ---- 3. RMS triangle amplitude ---- */
    float amp_tri = Measuring_Triangle_Amplitude(len, test_signal_raw);
    printf("RESULT:rms_triangle:%.6f\n", amp_tri);

    return 0;
}
