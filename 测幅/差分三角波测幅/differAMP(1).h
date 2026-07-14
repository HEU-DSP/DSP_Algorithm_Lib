#ifndef __DIFFERAMP_H
#define __DIFFERAMP_H
#include <stdint.h>
#include "arm_math.h"


//��ֲ����ǲ���ֵ
//����CPU�ڴ棬ʹ�ò�������Ϊ1024

void quick_sort_large(float32_t* arr, uint32_t length);
float Differ_Tri_Amp(uint16_t Length, uint16_t *AD_value);//���øú��������ǲ���ֵ��LengthΪ��������1024��AD_ValueΪ��������

#endif
