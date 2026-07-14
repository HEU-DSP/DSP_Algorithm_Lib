#include "MAG.h"
#include "math.h"  

//????????A??

float Measuring_Sine_Amplitude(uint16_t length,uint16_t *AD_value)
{
	uint16_t i,A=2;
	float C,temp,input,output;
	float sum = 0;
	C=3.3/4096;
	sum = 0;
	for(i=0;i<=length;i++)
	{
		sum = sum+AD_value[i];
	}
	sum = sum/length;
	for(i=0;i<=length;i++)
	{
		temp=temp+(AD_value[i]-sum)*(AD_value[i]-sum)*C*C;
	}
	input=A*temp/length;
	output=sqrt(input);
	return output;
}

float Measuring_Square_Amplitude(uint16_t length,uint16_t *AD_value)
{
	uint16_t i,A=1;
	float C,temp,input,output;
	float sum = 0;
	C=3.3/4096;
	sum = 0;
	for(i=0;i<=length;i++)
	{
		sum = sum+AD_value[i];
	}
	sum = sum/length;
	for(i=0;i<=length;i++)
	{
		temp=temp+(AD_value[i]-sum)*(AD_value[i]-sum)*C*C;
	}
	input=A*temp/length;
	output=sqrt(input);
	return output;
}

float Measuring_Triangle_Amplitude(uint16_t length,uint16_t *AD_value)
{
	uint16_t i,A=3;
	float C,temp,input,output;
	float sum = 0;
	C=3.3/4096;
	sum = 0;
	for(i=0;i<=length;i++)
	{
		sum = sum+AD_value[i];
	}
	sum = sum/length;
	for(i=0;i<=length;i++)
	{
		temp=temp+(AD_value[i]-sum)*(AD_value[i]-sum)*C*C;
	}
	input=A*temp/length;
	output=sqrt(input);
	return output;
}

