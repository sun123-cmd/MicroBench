#include "common.h"

// test 1: pure computation load - benchmark test
void test_pure_computation() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // warmup
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        volatile int a = 42, b = 17;
        volatile int c = a + b + a * b - (a % 7);
        result += c;
    }
    
    // main test
    for (int i = 0; i < ITERATIONS; i++) {
        unsigned long long start = get_timestamp();
        
        // fixed computation sequence
        volatile int a = 42 + (i & 0x7);  // slight change to avoid compiler optimization
        volatile int b = 17 + (i & 0x3);
        volatile int c = a + b;
        volatile int d = a * b;
        volatile int e = d - c;
        volatile int f = e % 13;
        volatile int g = f ^ a;
        result += g;
        
        unsigned long long end = get_timestamp();
        times[i] = end - start;
    }
    
    stats_t stats;
    calculate_stats(times, ITERATIONS, &stats);
    print_stats("Pure Computation", &stats);
}

// This file contains only the test function
// Main function is in microbench_main.c
