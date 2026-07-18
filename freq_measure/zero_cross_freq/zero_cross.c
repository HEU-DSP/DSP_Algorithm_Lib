/**
 * @file zero_cross.c
 * @brief Rising-edge zero-crossing frequency and period implementation.
 */

#include "zero_cross.h"

/*
 * Linear interpolation to find the precise zero-crossing point.
 * Between sample[i-1] (negative) and sample[i] (positive):
 *   t_cross = (i-1) + |sample[i-1]| / (|sample[i-1]| + |sample[i]|)
 */
static float interp_zero_cross(float32_t y_prev, float32_t y_curr)
{
    float denom = y_curr - y_prev;
    if (denom == 0.0f) return 0.0f;
    return -y_prev / denom;
}

int ZeroCross_Count(float32_t *input, int n)
{
    int count = 0;
    for (int i = 1; i < n; i++)
    {
        if (input[i - 1] <= 0 && input[i] > 0)
        {
            count++;
        }
    }
    return count;
}

float ZeroCross_Period(float32_t *input, int n, float fs)
{
    float first = -1.0f;
    float last = -1.0f;
    int count = 0;

    for (int i = 1; i < n; i++)
    {
        if (input[i - 1] <= 0 && input[i] > 0)
        {
            float frac = interp_zero_cross(input[i - 1], input[i]);
            float t = (float)(i - 1) + frac;

            if (first < 0.0f) first = t;
            last = t;
            count++;
        }
    }

    if (count < 2 || fs <= 0.0f) return 0.0f;

    /* Average all complete periods to reduce single-crossing noise jitter. */
    float period_samples = (last - first) / (float)(count - 1);
    return period_samples / fs;
}

float ZeroCross_Freq(float32_t *input, int n, float fs)
{
    float t_crossings[128];
    int count = 0;
    int max_store = (int)(sizeof(t_crossings) / sizeof(t_crossings[0]));

    for (int i = 1; i < n && count < max_store; i++)
    {
        if (input[i - 1] <= 0 && input[i] > 0)
        {
            float frac = interp_zero_cross(input[i - 1], input[i]);
            t_crossings[count] = (float)(i - 1) + frac;
            count++;
        }
    }

    if (count < 2) return 0.0f;

    float total_time = (t_crossings[count - 1] - t_crossings[0]) / fs;
    int periods = count - 1;
    float avg_period = total_time / (float)periods;

    return 1.0f / avg_period;
}
