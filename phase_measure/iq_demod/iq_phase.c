/**
 * @file iq_phase.c
 * @brief I/Q demodulation phase measurement implementation.
 */

#include "iq_phase.h"
#include "fft_buffer.h"
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
    if (input == NULL || output == NULL || n != SAMPLE_N) {
        return;
    }

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
    if (adc_float == NULL || f <= 0.0f || fs <= 0.0f || N <= 0 || f >= fs) {
        return 0.0f;
    }

    int samples_per_cycle = (int)(fs / f);
    if (samples_per_cycle < 1) {
        return 0.0f;
    }
    int k = N / samples_per_cycle;
    int N_new = k * samples_per_cycle;
    if (N_new <= 0 || N_new > SAMPLE_N) {
        return 0.0f;
    }

    float Ave = 0.0f;
    float i_signal = 0;
    float q_signal = 0;
    float t;

    for(int i = 0; i < N_new; i++)
    {
        Ave += adc_float[i];
    }
    Ave /= (float)N_new;

    for(int i = 0; i < N_new; i++)
    {
        t = (float)i / fs;
        ref_i[i] = cosf(2.0f * PI * f * t);
        ref_q[i] = sinf(2.0f * PI * f * t);
        i_signal += (adc_float[i] - Ave) * ref_i[i];
        q_signal += (adc_float[i] - Ave) * ref_q[i];
    }
    /* For x(t)=A*sin(wt+phase): <x,cos>=A/2*sin(phase),
       <x,sin>=A/2*cos(phase), hence phase=atan2(I,Q). */
    return atan2f(i_signal, q_signal);
}
