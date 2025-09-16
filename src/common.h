#ifndef COMMON_H
#define COMMON_H

#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>
#include <math.h>
#include <string.h>
#include <time.h>

#define ITERATIONS 2000
#define WARMUP_ITERATIONS 500

// get high precision timestamp - cross-platform implementation
static inline unsigned long long get_timestamp() {
#if defined(__x86_64__) || defined(__i386__)
    // x86/x86_64: use RDTSC instruction
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((unsigned long long)hi << 32) | lo;
#elif defined(__aarch64__) || defined(__arm__)
    // ARM/ARM64: use generic timer
    unsigned long long val;
    #ifdef __aarch64__
        // ARM64: use cntvct_el0 register
        __asm__ __volatile__("mrs %0, cntvct_el0" : "=r" (val));
    #else
        // ARM32: use PMU cycle counter (requires permission)
        // alternative: use clock_gettime
        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);
        val = (unsigned long long)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
    #endif
    return val;
#else
    // other architectures: use standard library functions
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (unsigned long long)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
#endif
}

// statistics analysis structure
typedef struct {
    unsigned long long min, max, avg;
    double std_dev;
    unsigned long long p95, p99;  // 95% and 99% percentile
    unsigned long long jitter;
} stats_t;

// function declarations
void calculate_stats(unsigned long long *times, int n, stats_t *stats);
void print_stats(const char *test_name, stats_t *stats);

#endif // COMMON_H
