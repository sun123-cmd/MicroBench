#include "common.h"

// test 2: regular branch pattern
void test_regular_branches() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // warmup
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        int x = i % 4;
        if (x == 0) result += 1;
        else if (x == 1) result += 2;
        else result += 3;
    }
    
    // main test
    for (int i = 0; i < ITERATIONS; i++) {
        unsigned long long start = get_timestamp();
        
        volatile int x = i % 4;
        if (x == 0) result += 1;
        else if (x == 1) result += 2;
        else if (x == 2) result += 3;
        else result += 4;
        
        unsigned long long end = get_timestamp();
        times[i] = end - start;
    }
    
    stats_t stats;
    calculate_stats(times, ITERATIONS, &stats);
    print_stats("Regular Branch Pattern", &stats);
}

// This file contains only the test function
// Main function is in microbench_main.c
