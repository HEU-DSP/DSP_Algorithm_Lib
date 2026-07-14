/*
*********************************************************************************************************
*
*	ģ������ : FFT
*	�ļ����� : FFTNt.h
*	��    �� : V2.0
*	˵    �� : �����Ƶ���FFT�������ɺ궨��MAX_FFT_N���á�
*              ��С֧��16�㣬���㲻�ޣ�����2^n���ɡ�
*
*
*********************************************************************************************************
*/
#ifndef __FFTNt_H_
#define __FFTNt_H_

#include <stdint.h>
#include <math.h>
#include "arm_math.h"

#define   MAX_FFT_N		 8192	

struct  compx 
{
	float32_t real, imag;
};   

void InitTableFFT(uint32_t n);
void cfft(struct compx *_ptr, uint32_t FFT_N );
int find_exponent(unsigned int n);
#endif