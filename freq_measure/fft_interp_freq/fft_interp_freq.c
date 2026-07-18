/**
 * @file fft_interp_freq.c
 * @brief FFT peak and log-parabolic interpolation frequency estimator.
 */

#include "fft_interp_freq.h"

#include "fft_n.h"
struct  compx s[MAX_FFT_N];
uint32_t temp_1;
float32_t f,temp1;
float cfft_f32_fre(float32_t fs,uint16_t *AD_Value,uint8_t flag)
{
	uint32_t i,j,k;
	float32_t magmax = 0.0f;

	InitTableFFT(MAX_FFT_N);

	for(i=0; i<MAX_FFT_N; i++)
	{
		/* ��������ֱ��������500Hz���Ҳ���ɣ����β�����MAX_FFT_N����ʼ��λ60�� */
		s[i].real = AD_Value[i];
		s[i].imag = 0;
	}

	/* MAX_FFT_N�����FFT */
	cfft(s, MAX_FFT_N);

	/* �����Ƶ */
	for(k=0; k<MAX_FFT_N; k++)
	{
		arm_sqrt_f32((float32_t)(s[k].real *s[k].real+ s[k].imag*s[k].imag ), &s[k].real);
	}

	/* ���ڴ�ӡ���ķ�Ƶ */
	temp_1 = 2U;
	for(j=2; j<MAX_FFT_N/2; j++)
	{
		if(s[j].real > magmax)
			{
				 magmax = s[j].real;
				 temp_1 = j;
			}
	}

  if(flag==1)
	{

	/* Log-parabolic interpolation reduces the large rectangular-window bias
	   of a quadratic fit to linear magnitudes. */
	const float32_t left = logf(fmaxf(s[temp_1 - 1U].real, 1.0e-12f));
	const float32_t peak = logf(fmaxf(s[temp_1].real, 1.0e-12f));
	const float32_t right = logf(fmaxf(s[temp_1 + 1U].real, 1.0e-12f));
	const float32_t denominator = left - 2.0f * peak + right;
	float32_t delta = 0.0f;
	if (fabsf(denominator) > 1.0e-12f) {
		delta = 0.5f * (left - right) / denominator;
	}
	temp1 = (float32_t)temp_1 + delta;
	f = temp1 * fs / MAX_FFT_N;
	return f;

	}

	 if(flag==2)
	{

	f=temp_1*fs/MAX_FFT_N;
	return f;

	}

	return 0.0f;


}
