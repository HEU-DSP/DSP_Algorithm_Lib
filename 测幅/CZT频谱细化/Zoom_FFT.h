#ifndef _ZOOM_FFT_H_
#define _ZOOM_FFT_H_

#include <stdint.h>
#include <math.h>
#include "arm_math.h"

void czt_Init_0(float32_t *input, int FS,
        int f_start, int f_end,float32_t *zoom_abs/*P*/) ;
float czt_result_fre(int FS, int f_start, int f_end,float32_t *zoom_abs/*P*/);
float czt_Amp(int FS, int f_start, int f_end,float32_t *zoom_abs/*P*/);
float czt_Phase(int FS, int f_start, int f_end,float32_t *zoom_abs/*P*/);


#endif 




