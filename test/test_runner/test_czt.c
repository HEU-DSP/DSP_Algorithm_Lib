/**
 * test_czt.c — CZT 频谱细化测试
 *
 * 被测函数：
 *   - czt_Init_0(input, FS, f_start, f_end, zoom_abs) — CZT 初始化
 *   - czt_result_fre(FS, f_start, f_end, zoom_abs)    — CZT 频率估计
 *   - czt_Amp(FS, f_start, f_end, zoom_abs)            — CZT 幅度估计
 *   - czt_Phase(FS, f_start, f_end, zoom_abs)          — CZT 相位估计
 *
 * 注意：czt_zoom_fft.c 硬编码 N=2048, M=2048, P=4096。
 *       信号长度必须 ≥ N。
 */
#include <stdio.h>
#include <stdint.h>
#include "arm_math.h"
#include "signal_data.h"
#include "czt_zoom_fft.h"

#define CZT_M    2048

#if SIGNAL_LENGTH != CZT_M
#error "test_czt requires SIGNAL_LENGTH == 2048"
#endif

int main(void)
{
    /* CZT refines around SIGNAL_FREQ +/- 100 Hz */
    int f_start = (int)SIGNAL_FREQ - 100;
    int f_end   = (int)SIGNAL_FREQ + 100;
    if (f_start < 0) f_start = 0;

    float32_t zoom_abs[CZT_M];

    /* ---- 1. CZT init ---- */
    czt_Init_0(test_signal_float, (int)SIGNAL_FS, f_start, f_end, zoom_abs);

    /* ---- 2. CZT frequency estimation ---- */
    float czt_f = czt_result_fre((int)SIGNAL_FS, f_start, f_end, zoom_abs);
    printf("RESULT:czt_freq:%.6f\n", czt_f);

    /* ---- 3. CZT amplitude estimation ---- */
    float czt_a = czt_Amp((int)SIGNAL_FS, f_start, f_end, zoom_abs);
    printf("RESULT:czt_amp:%.6f\n", czt_a);

    /* ---- 4. CZT phase estimation ---- */
    float czt_p = czt_Phase((int)SIGNAL_FS, f_start, f_end, zoom_abs);
    printf("RESULT:czt_phase:%.6f\n", czt_p);

    return 0;
}
