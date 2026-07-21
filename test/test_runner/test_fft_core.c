#include <math.h>
#include <stdio.h>
#include <time.h>

#include "benchmark.h"
#include "fft_n.h"
#include "signal_data.h"

#if SIGNAL_LENGTH != MAX_FFT_N
#error "test_fft_core requires SIGNAL_LENGTH == MAX_FFT_N"
#endif

#define FFT_CORE_BENCHMARK_ITERATIONS 40U

static struct compx fft_buffer[SIGNAL_LENGTH];

static void measure_fft_core(float32_t *frequency, float32_t *magnitude)
{
    uint32_t bin;
    uint32_t peak_bin = 1U;
    float32_t peak_magnitude = 0.0f;

    for (bin = 0U; bin < SIGNAL_LENGTH; ++bin) {
        fft_buffer[bin].real = test_signal_float[bin];
        fft_buffer[bin].imag = 0.0f;
    }

    cfft(fft_buffer, SIGNAL_LENGTH);

    for (bin = 1U; bin < SIGNAL_LENGTH / 2U; ++bin) {
        const float32_t bin_magnitude = sqrtf(
            fft_buffer[bin].real * fft_buffer[bin].real +
            fft_buffer[bin].imag * fft_buffer[bin].imag);
        if (bin_magnitude > peak_magnitude) {
            peak_magnitude = bin_magnitude;
            peak_bin = bin;
        }
    }

    *frequency = (float32_t)peak_bin * SIGNAL_FS / (float32_t)SIGNAL_LENGTH;
    *magnitude = peak_magnitude;
}

int main(void)
{
    clock_t begin;
    clock_t end;
    float32_t frequency;
    float32_t magnitude;
    volatile float32_t benchmark_sink = 0.0f;
    unsigned int iteration;

    if (SIGNAL_FREQ <= 0.0f) {
        return 2;
    }

    InitTableFFT(SIGNAL_LENGTH);
    measure_fft_core(&frequency, &magnitude);
    printf("RESULT:fft_core_freq:%.6f\n", frequency);
    printf("RESULT:fft_core_magnitude:%.6f\n", magnitude);

    /*
     * The benchmark deliberately includes copying the deterministic test
     * signal into the mutable FFT buffer before every transform.
     */
    measure_fft_core(&frequency, &magnitude);
    begin = clock();
    for (iteration = 0U; iteration < FFT_CORE_BENCHMARK_ITERATIONS; ++iteration) {
        measure_fft_core(&frequency, &magnitude);
        benchmark_sink += frequency + magnitude;
    }
    end = clock();

    if (benchmark_sink == -1.0f) {
        return 3;
    }
    printf("BENCH:fft_core:%u:%.6f\n", FFT_CORE_BENCHMARK_ITERATIONS,
           benchmark_average_us(begin, end, FFT_CORE_BENCHMARK_ITERATIONS));
    return 0;
}
