/**
 * @file fft_n.c
 * @brief In-place radix-2 complex FFT implementation.
 */

#include "fft_n.h"
/* Twiddle-factor lookup tables for the FFT length. */
float32_t   costab[MAX_FFT_N/2];
float32_t   sintab[MAX_FFT_N/2];
void InitTableFFT(uint32_t n)
{
	uint32_t i;

/* Precompute sine and cosine twiddle factors. */

	for (i = 0; i < n/2; i ++ )
	{
		sintab[ i ]=  sin( 2 * PI * i / MAX_FFT_N );
		costab[ i ]=  cos( 2 * PI * i / MAX_FFT_N );
	}

}
/* Return floor(log2(m)); zero has no valid exponent. */
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


/* Iterative radix-2 complex FFT with bit-reversed input ordering. */
int index1;
void cfft(struct compx *_ptr, uint32_t FFT_N )
{
	float32_t TempReal1, TempImag1, TempReal2, TempImag2;
	uint32_t k,i,j,z;
	uint32_t Butterfly_NoPerColumn;				    /* Number of butterfly groups in this stage. */
	uint32_t Butterfly_NoOfGroup;					/* Index of the current butterfly group. */
	uint32_t Butterfly_NoPerGroup;					/* Number of sample offsets within each group. */
	uint32_t ButterflyIndex1,ButterflyIndex2,P,J;
	uint32_t L;
	uint32_t M;
  index1 = find_exponent(FFT_N);
	z=FFT_N/2;                  					/* Initial mask for bit-reversal indexing. */
	for(i=0,j=0;i<FFT_N-1;i++)
	{
		/* Put input samples into bit-reversed order before FFT stages. */
		if(i<j)
		{
			TempReal1  = _ptr[j].real;
			_ptr[j].real= _ptr[i].real;
			_ptr[i].real= TempReal1;
		}

		k=z;                    				  /* Start bit-reversal carry propagation. */

		while(k<=j)               				  /* Clear trailing set bits in reversed index. */
		{
			j=j-k;                 				  /* Clear the current index bit. */
			k=k/2;                 				  /* Move the carry to the next bit. */
		}

		j=j+k;                   				  /* Set the first cleared reversed-index bit. */
	}

	/* Each radix-2 stage halves the group count and doubles group width. */
	/* Butterfly_NoPerColumn gives the current stage's group count. */
	/* Butterfly_NoPerGroup gives the spacing of paired samples. */
	Butterfly_NoPerColumn = FFT_N;
	Butterfly_NoPerGroup = 1;
	M =index1;
	for ( L = 0;L < M; L++ )
	{
		Butterfly_NoPerColumn >>= 1;		/* For N=8, group count evolves as 4, 2, 1. */

		/* Process every butterfly group in this stage. */
		for ( Butterfly_NoOfGroup = 0;Butterfly_NoOfGroup < Butterfly_NoPerColumn;Butterfly_NoOfGroup++ )
		{
			for ( J = 0;J < Butterfly_NoPerGroup;J ++ )	    /* Offset of a paired sample in a group. */
			{					   						    /* Combine the pair with one radix-2 butterfly. */
				ButterflyIndex1 = ( ( Butterfly_NoOfGroup * Butterfly_NoPerGroup ) << 1 ) + J;/* (0,2,4,6)(0,1,4,5)(0,1,2,3) */
				ButterflyIndex2 = ButterflyIndex1 + Butterfly_NoPerGroup;/* Second input of the butterfly pair. */
				P = J * Butterfly_NoPerColumn;				/* Lookup index for the stage rotation factor. */

				/* Rotate the second sample by its twiddle factor. */
				TempReal2 = _ptr[ButterflyIndex2].real * costab[ P ] +  _ptr[ButterflyIndex2].imag * sintab[ P ];
				TempImag2 = _ptr[ButterflyIndex2].imag * costab[ P ] -  _ptr[ButterflyIndex2].real * sintab[ P ] ;
				TempReal1 = _ptr[ButterflyIndex1].real;
				TempImag1 = _ptr[ButterflyIndex1].imag;

				/* Store the sum and difference butterfly outputs. */
				_ptr[ButterflyIndex1].real = TempReal1 + TempReal2;
				_ptr[ButterflyIndex1].imag = TempImag1 + TempImag2;
				_ptr[ButterflyIndex2].real = TempReal1 - TempReal2;
				_ptr[ButterflyIndex2].imag = TempImag1 - TempImag2;
			}
		}

		Butterfly_NoPerGroup<<=1;							/* Double pair spacing for the next stage. */
	}
}
