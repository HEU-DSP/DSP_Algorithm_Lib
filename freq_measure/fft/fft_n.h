/**
 * @file fft_n.h
 * @brief In-place radix-2 complex FFT interfaces.
 */

#ifndef FFT_N_H
#define FFT_N_H

#include <stdint.h>

#include "arm_math.h"

#define MAX_FFT_N 8192U

/** Complex sample used by the legacy FFT implementation. */
struct compx {
    float32_t real;
    float32_t imag;
};

/**
 * @brief Initialize sine and cosine lookup tables for an FFT length.
 * @param[in] n Number of lookup-table samples to initialize.
 */
void InitTableFFT(uint32_t n);

/**
 * @brief Execute an in-place radix-2 complex FFT.
 * @param[in,out] _ptr Complex input and output buffer.
 * @param[in] FFT_N Transform length; must be a power of two not exceeding MAX_FFT_N.
 */
void cfft(struct compx *_ptr, uint32_t FFT_N);

/**
 * @brief Return floor(log2(n)).
 * @param[in] n Positive integer input.
 * @return Base-2 exponent, or -1 when n is zero.
 */
int find_exponent(unsigned int n);

#endif /* FFT_N_H */
