#include <stdio.h>
#include "arm_math.h"

int main() {
    float32_t x = 4.0f;
    float32_t result;
    arm_sqrt_f32(x, &result);
    printf("RESULT:sanity_sqrt:%f\n", result);
    return 0;
}
