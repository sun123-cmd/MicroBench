#include "common.h"

// test 6: high frequency branches (simulate loop)
void test_high_frequency_branches() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // warmup
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        for (int j = 0; j < 5; j++) {
            if (j & 1) result++;
        }
    }
    
    // main test - inner has multiple branches
    for (int i = 0; i < ITERATIONS; i++) {
        unsigned long long start = get_timestamp();
        
        volatile int count = 0;
        for (int j = 0; j < 8; j++) {
            if (j & 1) count++;
            if (j & 2) count += 2;
            if (j & 4) count += 4;
        }
        result += count;
        
        unsigned long long end = get_timestamp();
        times[i] = end - start;
    }
    
    stats_t stats;
    calculate_stats(times, ITERATIONS, &stats);
    print_stats("High-Frequency Branches", &stats);
}

// This file contains only the test function
// Main function is in microbench_main.c
