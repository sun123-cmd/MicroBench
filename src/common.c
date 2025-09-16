#include "common.h"

// calculate statistics
void calculate_stats(unsigned long long *times, int n, stats_t *stats) {
    // sort for calculating percentile
    unsigned long long sorted[n];
    memcpy(sorted, times, n * sizeof(unsigned long long));
    
    // simple bubble sort
    for (int i = 0; i < n-1; i++) {
        for (int j = 0; j < n-i-1; j++) {
            if (sorted[j] > sorted[j+1]) {
                unsigned long long temp = sorted[j];
                sorted[j] = sorted[j+1];
                sorted[j+1] = temp;
            }
        }
    }
    
    stats->min = sorted[0];
    stats->max = sorted[n-1];
    stats->jitter = stats->max - stats->min;
    
    // calculate average
    unsigned long long sum = 0;
    for (int i = 0; i < n; i++) {
        sum += times[i];
    }
    stats->avg = sum / n;
    
    // calculate standard deviation
    double variance = 0;
    for (int i = 0; i < n; i++) {
        double diff = (double)times[i] - (double)stats->avg;
        variance += diff * diff;
    }
    variance /= n;
    stats->std_dev = sqrt(variance);
    
    // calculate percentile
    stats->p95 = sorted[(int)(n * 0.95)];
    stats->p99 = sorted[(int)(n * 0.99)];
}

void print_stats(const char *test_name, stats_t *stats) {
    printf("=== %s ===\n", test_name);
    printf("  Min: %llu, Max: %llu, Avg: %llu\n", 
           stats->min, stats->max, stats->avg);
    printf("  Jitter: %llu, Std Dev: %.2f\n", 
           stats->jitter, stats->std_dev);
    printf("  95th percentile: %llu, 99th percentile: %llu\n", 
           stats->p95, stats->p99);
    printf("  Coefficient of Variation: %.4f\n", 
           stats->std_dev / stats->avg);
    printf("\n");
}
