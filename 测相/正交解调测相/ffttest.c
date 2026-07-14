#include "ffttest.h"
#include "data.h"
#include "arm_math.h"
#include "arm_const_structs.h"
#include <math.h>

static float ref_i[SAMPLE_N];
static float ref_q[SAMPLE_N];

void Create_data2handle(float32_t *p)
{
    for(int i = 0;i < SAMPLE_N; i++)
    {
        data2handle[2 * i]     = p[i];
        data2handle[2 * i + 1] = 0;
    }
}

void CalXiebo(float32_t *input, float32_t *output, int n)
{
    float32_t temp[2 * SAMPLE_N];
    for(int i = 0; i < n; i++)
    {
        temp[2 * i]     = input[i];
        temp[2 * i + 1] = 0;
    }
    arm_cfft_f32(&arm_cfft_sR_f32_len1024, temp, 0, 1);
    arm_cmplx_mag_f32(temp, output, n);
}

float CalPhase(float f, float fs, int N, float32_t *adc_float)
{
    int Ave = 0;
    int samples_per_cycle = (int)(fs / f);
    int k = N / samples_per_cycle;
    int N_new = k * samples_per_cycle;
    float i_signal = 0;
    float q_signal = 0;
    float t;

    for(int i = 0; i < N_new; i++)
    {
        Ave += (int)adc_float[i];
    }
    Ave = Ave / N_new;

    for(int i = 0; i < N_new; i++)
    {
        t = (float)i / fs;
        ref_i[i] = cosf(2.0f * PI * f * t);
        ref_q[i] = sinf(2.0f * PI * f * t);
        i_signal += (adc_float[i] - (float)Ave) * ref_i[i];
        q_signal += (adc_float[i] - (float)Ave) * ref_q[i];
    }
    return atan2f(q_signal, i_signal);
}
