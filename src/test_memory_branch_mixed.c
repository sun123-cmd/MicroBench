#include "common.h"

// test 5: memory access + branch mixed
void test_memory_branch_mixed() {
    static volatile int array[1024] __attribute__((aligned(64)));
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // initialize array
    for (int i = 0; i < 1024; i++) {
        array[i] = i % 100;
    }
    
    // warmup
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        int idx = i % 64;
        int val = array[idx];
        if (val > 50) result += val;
        else result -= val;
    }
    
    // main test - memory access result affects branch
    for (int i = 0; i < ITERATIONS; i++) {
        unsigned long long start = get_timestamp();
        
        volatile int idx1 = i % 128;
        volatile int idx2 = (i * 3) % 256;
        volatile int val1 = array[idx1];
        volatile int val2 = array[idx2];
        
        if (val1 > val2) {
            result += array[(val1 + val2) % 512];
        } else {
            result -= array[(val1 - val2 + 256) % 512];
        }
        
        unsigned long long end = get_timestamp();
        times[i] = end - start;
    }
    
    stats_t stats;
    calculate_stats(times, ITERATIONS, &stats);
    print_stats("Memory + Branch Mixed", &stats);
}

// This file contains only the test function
// Main function is in microbench_main.c
