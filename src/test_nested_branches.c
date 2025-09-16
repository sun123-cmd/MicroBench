#include "common.h"

// test 4: complex nested branches
void test_nested_branches() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // warmup
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        int x = i % 8;
        if (x > 4) {
            if (x > 6) result += 1;
            else result += 2;
        } else {
            if (x > 2) result += 3;
            else result += 4;
        }
    }
    
    // main test - nested branches increase prediction difficulty
    for (int i = 0; i < ITERATIONS; i++) {
        unsigned long long start = get_timestamp();
        
        volatile int x = (i * 7 + 3) % 16;  // more complex pattern
        
        if (x > 8) {
            if (x > 12) {
                result += (x & 0x1) ? 1 : 2;
            } else {
                result += (x & 0x2) ? 3 : 4;
            }
        } else {
            if (x > 4) {
                result += (x & 0x4) ? 5 : 6;
            } else {
                result += (x & 0x8) ? 7 : 8;
            }
        }
        
        unsigned long long end = get_timestamp();
        times[i] = end - start;
    }
    
    stats_t stats;
    calculate_stats(times, ITERATIONS, &stats);
    print_stats("Nested Branch Pattern", &stats);
}

// This file contains only the test function
// Main function is in microbench_main.c
