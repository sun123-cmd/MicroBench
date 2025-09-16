# MicroBench: Real-time Determinism CPU Benchmark

## Overview

MicroBench is a scientific real-time determinism test suite designed to evaluate CPU predictability under various computational and branch patterns. It measures execution time characteristics using high-precision timing (RDTSC) to assess real-time performance capabilities of different CPU architectures.

## Test Cases

### 1. Pure Computation
**Purpose**: Baseline test for pure computational workload without branches
**Implementation**:
- Fixed arithmetic sequence: addition, multiplication, subtraction, modulo, XOR operations
- Uses `volatile` variables to prevent compiler optimizations
- Minimal variation in input (`i & 0x7`, `i & 0x3`) to avoid excessive compiler optimization
- Expected behavior: Most deterministic performance due to absence of branch mispredictions

### 2. Regular Branch Pattern
**Purpose**: Tests predictable branch patterns that branch predictors can learn
**Implementation**:
- Simple modulo-4 pattern: `i % 4`
- Four predictable conditional branches in sequence
- TAGE branch predictor should learn this pattern effectively
- Expected behavior: Good predictability after warmup phase

### 3. Pseudo-Random Branch Pattern
**Purpose**: Tests unpredictable branch patterns that challenge branch predictors
**Implementation**:
- Linear Congruential Generator (LCG): `seed = seed * 1664525 + 1013904223`
- Pseudo-random modulo-7 pattern with multiple nested conditions
- Designed to defeat branch prediction mechanisms
- Expected behavior: Higher variance due to frequent branch mispredictions

### 4. Nested Branch Pattern
**Purpose**: Tests complex nested conditional structures
**Implementation**:
- Complex modulo-16 pattern: `(i * 7 + 3) % 16`
- Multi-level nested if-else structures (up to 3 levels deep)
- Bit manipulation conditions (`x & 0x1`, `x & 0x2`, etc.)
- Expected behavior: Moderate to high variance depending on prediction capability

### 5. Memory + Branch Mixed
**Purpose**: Tests data-dependent branch patterns combined with memory access
**Implementation**:
- 1024-element aligned array with cache-friendly access patterns
- Branch decisions based on memory values: `if (val1 > val2)`
- Secondary memory accesses dependent on branch outcomes
- Expected behavior: Variable performance due to cache effects and data-dependent branches

### 6. High-Frequency Branches
**Purpose**: Tests performance under high branch density
**Implementation**:
- Inner loop with 8 iterations containing multiple conditional statements
- Three simultaneous bit-test conditions per iteration
- Fixed, predictable pattern that should be well-predicted
- Expected behavior: Very stable performance due to predictable pattern and potential loop unrolling

## Output Metrics

The benchmark calculates and reports the following statistical metrics for each test case:

### Core Timing Metrics
- **Min**: Minimum execution time (CPU cycles)
- **Max**: Maximum execution time (CPU cycles)
- **Avg**: Average execution time (CPU cycles)

### Variability Metrics
- **Jitter**: Execution time variation (Max - Min), measures absolute timing uncertainty
- **Standard Deviation**: Measures dispersion of execution times around the mean
- **Coefficient of Variation**: Normalized variability (Std Dev / Average), enables comparison across different workloads

### Real-time Performance Indicators
- **95th Percentile**: 95% of executions complete within this time
- **99th Percentile**: 99% of executions complete within this time (tail latency)

## Real-time Significance

### Primary Real-time Metrics (Beyond Jitter)
1. **Standard Deviation**: Lower values indicate more predictable execution times
2. **Coefficient of Variation**: Best metric for comparing relative stability across different workloads
3. **95th/99th Percentiles**: Critical for real-time deadline analysis and worst-case execution time (WCET) estimation
4. **Max/Avg Ratio**: Indicates the gap between typical and worst-case performance

### Expected Results Ranking (Best to Worst Real-time Performance)
1. **High-Frequency Branches**: Extremely stable due to predictable patterns
2. **Pure Computation**: Minimal variance from deterministic arithmetic
3. **Regular Branch Pattern**: Good predictability after pattern learning
4. **Memory + Branch Mixed**: Moderate stability affected by cache behavior
5. **Nested Branch Pattern**: Variable due to complex prediction requirements
6. **Pseudo-Random Branch Pattern**: Worst stability due to unpredictable branches

## Usage

### Quick Start (Recommended)
```bash
# Run complete benchmark and analysis from root directory
./run_benchmark.sh
```

### Statistical Multi-Run Testing (Recommended for Research)
For statistically significant results, use the multi-run controlled test that performs multiple iterations with statistical analysis:

```bash
# Run 20 controlled tests with statistical analysis (default)
cd tools
./run_controlled_test.sh

# Custom number of runs and sleep interval
./run_controlled_test.sh -n 50 -s 10    # 50 runs with 10-second intervals
./run_controlled_test.sh -n 10 -s 3     # 10 runs with 3-second intervals

# View help for all options
./run_controlled_test.sh --help
```

**Multi-run features:**
- **Automatic CPU affinity setting** to ensure consistent execution environment
- **Configurable number of runs** (default: 20) for statistical significance
- **Adjustable sleep intervals** between runs to avoid thermal effects
- **Comprehensive statistical analysis** including:
  - Mean, standard deviation, and confidence intervals (95%)
  - Coefficient of variation for stability assessment
  - Cross-run consistency scoring
  - Statistical visualization charts
- **Organized output** in timestamped directories with all data and charts

### Manual Execution
```bash
# Step 1: Compile (if needed)
cd src
./build.sh

# Step 2: Run benchmark
cd ../bin
./microbench > ../result/my_results.txt

# Step 3: Analyze results  
cd ../tools
python analyze_results.py ../result/my_results.txt -o ../result/my_analysis.csv
```

### Analysis Only
```bash
# Analyze existing results (single run)
cd tools
python analyze_results.py ../result/existing_results.txt -o ../result/analysis.csv

# Analyze multi-run data
python analyze_results.py --multi-run ../result/multi_run_20250916_123456 -o multi_analysis.csv

# Skip visualization
python analyze_results.py ../result/results.txt --no-plot
```

## Technical Implementation Details

- **Timing Method**: RDTSC (Read Time-Stamp Counter) for cycle-accurate measurements
- **Warmup**: 500 iterations to ensure stable CPU state and cache warmup
- **Test Iterations**: 2000 iterations for statistical significance
- **Compiler Considerations**: Uses `volatile` keywords to prevent unwanted optimizations
- **Memory Alignment**: 64-byte alignment for cache line optimization

## Interpretation Guidelines

### Single Run Analysis
- **Lower jitter, standard deviation, and coefficient of variation** indicate better real-time determinism
- **Smaller gaps between percentiles and average** suggest more predictable worst-case behavior
- **Different test patterns stress different aspects** of the CPU's branch prediction and execution pipeline

### Multi-Run Statistical Analysis
When using the multi-run testing (`run_controlled_test.sh`), additional metrics help assess long-term stability:

- **Confidence Intervals (95%)**: Narrower intervals indicate more consistent performance across runs
- **Cross-Run Consistency Score**: Higher percentages (>90%) suggest excellent repeatability
- **Standard Deviation of Averages**: Lower values indicate stable performance over multiple test sessions
- **Coefficient of Variation Stability**: Consistent CV values across runs show predictable variability patterns

### Performance Ranking Interpretation
The multi-run analysis provides a **consistency score** that combines multiple factors:
- **Excellent (90-100%)**: Highly deterministic, suitable for hard real-time systems
- **Good (75-89%)**: Adequate for most real-time applications
- **Fair (60-74%)**: May require additional consideration for timing-critical applications
- **Poor (<60%)**: Not recommended for real-time use without further optimization

### Output Files Explanation
Multi-run testing generates several files in the `multi_run_TIMESTAMP/` directory:
- `run_X_TIMESTAMP.txt`: Raw benchmark data for each individual run
- `multi_run_analysis_TIMESTAMP.csv`: Comprehensive statistical analysis data
- `multi_run_analysis_TIMESTAMP.png`: Statistical visualization charts showing CPU model
- `multi_run_info.txt`: Experiment metadata and configuration details

**Results help characterize CPU suitability** for real-time applications requiring timing guarantees. The multi-run approach is particularly valuable for research, benchmarking different CPU configurations, and validating real-time system designs.

This benchmark is particularly useful for evaluating CPU architectures in embedded systems, real-time control systems, and any application where timing predictability is critical.
