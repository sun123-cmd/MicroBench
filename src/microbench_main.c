#include "common.h"

extern void test_pure_computation();
extern void test_regular_branches();
extern void test_pseudo_random_branches();
extern void test_nested_branches();
extern void test_memory_branch_mixed();
extern void test_high_frequency_branches();

int main() {
    printf("Scientific Real-time Determinism Test\n");
    printf("Testing CPU predictability under various branch patterns\n");
    printf("Iterations: %d (+ %d warmup)\n\n", ITERATIONS, WARMUP_ITERATIONS);
    
    test_pure_computation();
    test_regular_branches();
    test_pseudo_random_branches();
    test_nested_branches();
    test_memory_branch_mixed();
    test_high_frequency_branches();
    
    return 0;
}
