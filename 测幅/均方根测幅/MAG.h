#ifndef __MAG_H
#define __MAG_H
#include <stdint.h>

//length��ָ�����С���漰��������������AD_value�ǲ����ĵ�ѹֵ����
float Measuring_Sine_Amplitude(uint16_t length,uint16_t *AD_value);//����
float Measuring_Square_Amplitude(uint16_t length,uint16_t *AD_value);//����
float Measuring_Triangle_Amplitude(uint16_t length,uint16_t *AD_value);//���ǲ�
#endif
