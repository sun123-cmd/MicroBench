#include <stdio.h>
#include <stdlib.h>
#include <sys/time.h>
#include <unistd.h>
#include <math.h>
#include <string.h>
#include <time.h>

#define ITERATIONS 2000
#define WARMUP_ITERATIONS 500

// 获取高精度时间戳 - 跨平台实现
static inline unsigned long long get_timestamp() {
#if defined(__x86_64__) || defined(__i386__)
    // x86/x86_64: 使用RDTSC指令
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((unsigned long long)hi << 32) | lo;
#elif defined(__aarch64__) || defined(__arm__)
    // ARM/ARM64: 使用通用计时器
    unsigned long long val;
    #ifdef __aarch64__
        // ARM64: 使用cntvct_el0寄存器
        __asm__ __volatile__("mrs %0, cntvct_el0" : "=r" (val));
    #else
        // ARM32: 使用PMU cycle counter (需要权限)
        // 备选方案：使用clock_gettime
        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);
        val = (unsigned long long)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
    #endif
    return val;
#else
    // 其他架构: 使用标准库函数
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (unsigned long long)ts.tv_sec * 1000000000ULL + ts.tv_nsec;
#endif
}

// 统计分析结构
typedef struct {
    unsigned long long min, max, avg;
    double std_dev;
    unsigned long long p95, p99;  // 95%和99%分位数
    unsigned long long jitter;
} stats_t;

// 计算统计信息
void calculate_stats(unsigned long long *times, int n, stats_t *stats) {
    // 排序用于计算分位数
    unsigned long long sorted[n];
    memcpy(sorted, times, n * sizeof(unsigned long long));
    
    // 简单冒泡排序
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
    
    // 计算平均值
    unsigned long long sum = 0;
    for (int i = 0; i < n; i++) {
        sum += times[i];
    }
    stats->avg = sum / n;
    
    // 计算标准差
    double variance = 0;
    for (int i = 0; i < n; i++) {
        double diff = (double)times[i] - (double)stats->avg;
        variance += diff * diff;
    }
    variance /= n;
    stats->std_dev = sqrt(variance);
    
    // 计算分位数
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

// 测试1：纯计算负载 - 基准测试
void test_pure_computation() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // 预热
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        volatile int a = 42, b = 17;
        volatile int c = a + b + a * b - (a % 7);
        result += c;
    }
    
    // 正式测试
    for (int i = 0; i < ITERATIONS; i++) {
        unsigned long long start = get_timestamp();
        
        // 固定计算序列
        volatile int a = 42 + (i & 0x7);  // 轻微变化避免编译器优化
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

// 测试2：规律分支模式
void test_regular_branches() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // 预热
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        int x = i % 4;
        if (x == 0) result += 1;
        else if (x == 1) result += 2;
        else result += 3;
    }
    
    // 正式测试 - 4的倍数循环，TAGE应该能学习
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

// 测试3：伪随机分支模式
void test_pseudo_random_branches() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // 使用线性同余生成器产生伪随机数
    unsigned int seed = 12345;
    
    // 预热
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        seed = seed * 1664525 + 1013904223;
        if (seed & 0x1) result += 1;
        else result += 2;
    }
    
    // 正式测试 - 难以预测的分支模式
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

// 测试4：复杂嵌套分支
void test_nested_branches() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // 预热
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
    
    // 正式测试 - 嵌套分支增加预测难度
    for (int i = 0; i < ITERATIONS; i++) {
        unsigned long long start = get_timestamp();
        
        volatile int x = (i * 7 + 3) % 16;  // 更复杂的模式
        
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

// 测试5：内存访问 + 分支混合
void test_memory_branch_mixed() {
    static volatile int array[1024] __attribute__((aligned(64)));
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // 初始化数组
    for (int i = 0; i < 1024; i++) {
        array[i] = i % 100;
    }
    
    // 预热
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        int idx = i % 64;
        int val = array[idx];
        if (val > 50) result += val;
        else result -= val;
    }
    
    // 正式测试 - 内存访问结果影响分支
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

// 测试6：高频分支（模拟循环）
void test_high_frequency_branches() {
    unsigned long long times[ITERATIONS];
    volatile int result = 0;
    
    // 预热
    for (int i = 0; i < WARMUP_ITERATIONS; i++) {
        for (int j = 0; j < 5; j++) {
            if (j & 1) result++;
        }
    }
    
    // 正式测试 - 内层有多个分支
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
    
    // printf("Analysis Notes:\n");
    // printf("- Lower jitter and std dev indicate better determinism\n");
    // printf("- Coefficient of Variation shows relative variability\n");
    // printf("- 99th percentile shows worst-case behavior\n");
    // printf("- Different patterns test different aspects of branch prediction\n");
    
    return 0;
}
