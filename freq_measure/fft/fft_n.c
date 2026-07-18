/**
 * @file fft_n.c
 * @brief In-place radix-2 complex FFT implementation.
 */

#include "fft_n.h"
/*
*********************************************************************************************************
*	�� �� ��: Int_FFT_TAB
*	����˵��: ���Һ����ұ�
*	��    ��: FFT����
*	�� �� ֵ: ��
*********************************************************************************************************
*/
float32_t   costab[MAX_FFT_N/2];
float32_t   sintab[MAX_FFT_N/2];
void InitTableFFT(uint32_t n)
{
	uint32_t i;

/* ����ʹ�������ȡcos��sinֵ */

	for (i = 0; i < n/2; i ++ )
	{
		sintab[ i ]=  sin( 2 * PI * i / MAX_FFT_N );
		costab[ i ]=  cos( 2 * PI * i / MAX_FFT_N );
	}

}
/*
*********************************************************************************************************
*	�� �� ��: find_exponent
*	����˵��: ������2Ϊ�׵Ķ���
*	��    ��: FFT����
*	�� �� ֵ: ��2Ϊ�׵Ķ���
*********************************************************************************************************
*/
int find_exponent(unsigned int m) {

	  int exponent = 0;
	if (m == 0) {
        return -1;
    }


    while (m> 1) {
        m >>= 1;
        exponent++;
    }
    return exponent;
}


/*
*********************************************************************************************************
*	�� �� ��: cfft
*	����˵��: ������ĸ�������п��ٸ���Ҷ�任��FFT��
*	��    ��: *_ptr �����ṹ������׵�ַָ��struct��
*             FFT_N ��ʾ����
*	�� �� ֵ: ��
*********************************************************************************************************
*/
int index1;
void cfft(struct compx *_ptr, uint32_t FFT_N )
{
	float32_t TempReal1, TempImag1, TempReal2, TempImag2;
	uint32_t k,i,j,z;
	uint32_t Butterfly_NoPerColumn;				    /* ÿ�����εĵ������� */
	uint32_t Butterfly_NoOfGroup;					/* ������ĵڼ��� */
	uint32_t Butterfly_NoPerGroup;					/* ������ĵڼ������� */
	uint32_t ButterflyIndex1,ButterflyIndex2,P,J;
	uint32_t L;
	uint32_t M;
  index1 = find_exponent(FFT_N);
	z=FFT_N/2;                  					/* ��ַ���㣬������Ȼ˳���ɵ�λ�򣬲����׵��㷨 */
	for(i=0,j=0;i<FFT_N-1;i++)
	{
		/*
		  ���i<j,�����б�ַ i=j˵������������i>j˵��ǰ���Ѿ��任���ˣ������ٱ仯��ע������һ����ʵ�� ���������� ���óɽ����
		*/
		if(i<j)
		{
			TempReal1  = _ptr[j].real;
			_ptr[j].real= _ptr[i].real;
			_ptr[i].real= TempReal1;
		}

		k=z;                    				  /*��j����һ����λ�� */

		while(k<=j)               				  /* ���k<=j,��ʾj�����λΪ1 */
		{
			j=j-k;                 				  /* �����λ���0 */
			k=k/2;                 				  /* k/2���Ƚϴθ�λ���������ƣ�����Ƚϣ�ֱ��ĳ��λΪ0��ͨ�������Ǿ�j=j+kʹ���Ϊ1 */
		}

		j=j+k;                   				  /* ����һ������ţ������0�����0��Ϊ1 */
	}

	/* ��L������(M)��Butterfly_NoOfGroup��(Butterfly_NoPerColumn)��J������(Butterfly_NoPerGroup)****** */
	/* ���ε�������2�ı����ݼ�Butterfly_NoPerColumn��ÿ���е��εĸ�����2�ı�������Butterfly_NoPerGroup */
	/* �ڼ������ʱ��ÿL�еĵ�������,һ����M�У�ÿ������е��εĸ���,���εĽ���(0,1,2.....M-1) */
	Butterfly_NoPerColumn = FFT_N;
	Butterfly_NoPerGroup = 1;
	M =index1;
	for ( L = 0;L < M; L++ )
	{
		Butterfly_NoPerColumn >>= 1;		/* �������� ����N=8����(4,2,1) */

		/* ��L������ ��Butterfly_NoOfGroup��	��0,1��....Butterfly_NoOfGroup-1��*/
		for ( Butterfly_NoOfGroup = 0;Butterfly_NoOfGroup < Butterfly_NoPerColumn;Butterfly_NoOfGroup++ )
		{
			for ( J = 0;J < Butterfly_NoPerGroup;J ++ )	    /* �� Butterfly_NoOfGroup ���еĵ�J�� */
			{					   						    /* �� ButterflyIndex1 �͵� ButterflyIndex2 ��Ԫ������������,WNC */
				ButterflyIndex1 = ( ( Butterfly_NoOfGroup * Butterfly_NoPerGroup ) << 1 ) + J;/* (0,2,4,6)(0,1,4,5)(0,1,2,3) */
				ButterflyIndex2 = ButterflyIndex1 + Butterfly_NoPerGroup;/* ����Ҫ����������������Butterfly_NoPerGroup (ge=1,2,4) */
				P = J * Butterfly_NoPerColumn;				/* �����൱��P=J*2^(M-L),����һ�������±궼��N (0,0,0,0)(0,2,0,2)(0,1,2,3) */

				/* �����ת�����ӳ˻� */
				TempReal2 = _ptr[ButterflyIndex2].real * costab[ P ] +  _ptr[ButterflyIndex2].imag * sintab[ P ];
				TempImag2 = _ptr[ButterflyIndex2].imag * costab[ P ] -  _ptr[ButterflyIndex2].real * sintab[ P ] ;
				TempReal1 = _ptr[ButterflyIndex1].real;
				TempImag1 = _ptr[ButterflyIndex1].imag;

				/* �������� */
				_ptr[ButterflyIndex1].real = TempReal1 + TempReal2;
				_ptr[ButterflyIndex1].imag = TempImag1 + TempImag2;
				_ptr[ButterflyIndex2].real = TempReal1 - TempReal2;
				_ptr[ButterflyIndex2].imag = TempImag1 - TempImag2;
			}
		}

		Butterfly_NoPerGroup<<=1;							/* һ���е��εĸ���(1,2,4) */
	}
}
