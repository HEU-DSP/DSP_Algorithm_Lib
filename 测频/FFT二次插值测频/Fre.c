#include "fftnt.h"
#include "arm_math.h"
struct  compx s[MAX_FFT_N]; 
uint32_t temp_1;
float32_t f,temp1;                                 
float cfft_f32_fre(float32_t fs,uint16_t *AD_Value,uint8_t flag)
{
	uint32_t i,j,k,magmax;
	
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
	for(j=0; j<MAX_FFT_N/2; j++)
	{
		if(s[j].real > magmax && j > 1 )
			{
				 magmax = s[j].real;
				 temp_1 = j;
			}
	}
	
  if(flag==1)
	{
		
	temp1=(2*temp_1*(s[temp_1-1].real+s[temp_1+1].real-2*s[temp_1].real)+s[temp_1-1].real-s[temp_1+1].real)/2/(s[temp_1-1].real+s[temp_1+1].real-2*s[temp_1].real);
	f=temp1*fs/MAX_FFT_N;
	return f;
		
	}
	
	 if(flag==2)
	{
		
	f=temp_1*fs/MAX_FFT_N;
	return f;
		
	}
	
	
} 














































