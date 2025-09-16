#include "common.h"

// test 3: pseudo-random branch pattern
void test_pseudo_random_branches() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // use linear congruential generator to generate pseudo-random number
    unsigned int seed = 12345;
    
    // warmup
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        seed = seed * 1664525 + 1013904223;
        if (seed & 0x1) result += 1;
        else result += 2;
    }
    
    // main test - difficult to predict branch pattern
    for (int i = 0; i < ITERATIONS; i++) {
        unsigned long long start = get_timestamp();
        
        seed = seed * 1664525 + 1013904223;
        volatile int x = seed % 7;
        
        if (x < 2) result += 1;
        else if (x < 4) result += 2;
        else if (x < 6) result += 3;
        else result += 4;
        
        unsigned long long end = get_timestamp();
        times[i] = end - start;
    }
    
    stats_t stats;
    calculate_stats(times, ITERATIONS, &stats);
    print_stats("Pseudo-Random Branch Pattern", &stats);
}

// This file contains only the test function
// Main function is in microbench_main.c
