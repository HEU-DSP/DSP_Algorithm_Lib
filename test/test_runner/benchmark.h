#ifndef TEST_BENCHMARK_H
#define TEST_BENCHMARK_H

#include <time.h>

static inline double benchmark_average_us(clock_t begin, clock_t end,
                                          unsigned int iterations)
{
    return ((double)(end - begin) * 1000000.0) /
           ((double)CLOCKS_PER_SEC * (double)iterations);
}

#endif /* TEST_BENCHMARK_H */
