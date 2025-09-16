#!/bin/bash

echo "=== MicroBench Multiple Runs Controlled Test ==="
echo

# default configs
NUM_RUNS=20  # default 20 times
SLEEP_BETWEEN_RUNS=5  # default 5 seconds


while [[ $# -gt 0 ]]; do
    case $1 in
        -n|--num-runs)
            NUM_RUNS="$2"
            shift 2
            ;;
        -s|--sleep)
            SLEEP_BETWEEN_RUNS="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo "Options:"
            echo "  -n, --num-runs NUM     Number of test runs (default: 20)"
            echo "  -s, --sleep SECONDS    Sleep time between runs (default: 5)"
            echo "  -h, --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use -h or --help for usage information"
            exit 1
            ;;
    esac
done

echo "Config: Run $NUM_RUNS times, each interval $SLEEP_BETWEEN_RUNS seconds"
echo

if [[ $EUID -eq 0 ]]; then
    echo "Detecting root permissions, applying performance optimization settings"
    HAVE_ROOT=true
else
    echo "Non-root permissions, some optimization settings will be skipped"
    HAVE_ROOT=false
fi

# 1. 记录系统状态
echo "=== System Status Recording ==="
echo "Date: $(date)"
echo "Load: $(uptime)"
echo "CPU Frequency Strategy: $(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor 2>/dev/null || echo 'N/A')"
echo "Memory State: $(free -m | grep Mem:)"
echo

# 2. 设置CPU频率为性能模式（需要root）
if [ "$HAVE_ROOT" = true ]; then
    echo "Setting CPU to performance mode..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo performance > "$cpu" 2>/dev/null
    done
    echo "✓ CPU Frequency Strategy is set to performance"
else
    echo "⚠ Skipping CPU frequency setting (requires root permissions)"
fi

# 3. 设置进程优先级
echo "Setting high priority..."
renice -n -10 $$ 2>/dev/null && echo "✓ Process priority has been increased" || echo "⚠ Unable to increase process priority"

# 4. 清理系统缓存（需要root）
if [ "$HAVE_ROOT" = true ]; then
    echo "Cleaning system cache..."
    sync
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null && echo "✓ System cache has been cleaned" || echo "⚠ Unable to clean system cache"
fi

# 5. 设置CPU亲和性到单核
echo "Setting CPU affinity to CPU0..."
taskset -cp 0 $$ 2>/dev/null && echo "✓ CPU Affinity has been set" || echo "⚠ Unable to set CPU affinity"

# 6. 预热CPU（避免频率调节影响）
echo "CPU warming up..."
python3 -c "
import time
start = time.time()
while time.time() - start < 2:
    sum(i*i for i in range(1000))
print('✓ CPU warming up completed')
"

# 7. 运行多次基准测试
echo
echo "=== Start Controlled Benchmark Test (${NUM_RUNS} runs) ==="

# 检查microbench是否存在
if [ ! -f "../bin/microbench" ]; then
    echo "Error: microbench executable file does not exist"
    echo "Please run: cd ../src && bash build.sh"
    exit 1
fi

# 生成总时间戳和多次运行的实验目录
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
MULTI_RUN_DIR="../result/multi_run_${TIMESTAMP}"
mkdir -p "$MULTI_RUN_DIR"

echo "Multiple runs experiment directory: $MULTI_RUN_DIR"
echo "Start running $NUM_RUNS times..."
echo

# 存储每次运行的结果文件
RESULT_FILES=()
SUCCESS_COUNT=0

# 进行多次运行
for i in $(seq 1 $NUM_RUNS); do
    echo "=== Run $i/$NUM_RUNS ==="
    
    # 为每次运行生成独立的结果文件
    RUN_TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    TEMP_RESULTS_FILE="$MULTI_RUN_DIR/run_${i}_${RUN_TIMESTAMP}.txt"
    
    echo "Running test $i..."
    
    # 使用taskset确保在单核上运行
    if command -v taskset >/dev/null 2>&1; then
        taskset -c 0 ../bin/microbench > "$TEMP_RESULTS_FILE"
    else
        ../bin/microbench > "$TEMP_RESULTS_FILE"
    fi
    
    if [ $? -eq 0 ]; then
        echo "✓ Test $i completed"
        RESULT_FILES+=("$TEMP_RESULTS_FILE")
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "✗ Test $i failed"
        rm -f "$TEMP_RESULTS_FILE"
    fi
    
    # 在运行之间等待，除了最后一次
    if [ $i -lt $NUM_RUNS ]; then
        echo "Waiting ${SLEEP_BETWEEN_RUNS} seconds..."
        sleep $SLEEP_BETWEEN_RUNS
    fi
    
    echo
done

echo "=== Multiple runs completed ==="
echo "Successful runs: $SUCCESS_COUNT/$NUM_RUNS"

if [ $SUCCESS_COUNT -eq 0 ]; then
    echo "✗ All tests failed"
    exit 1
fi

echo
echo "=== Statistical analysis of multiple runs ==="

# 调用增强的分析工具进行多次运行统计分析
python3 analyze_results.py --multi-run "$MULTI_RUN_DIR" -o "multi_run_analysis_${TIMESTAMP}.csv"

if [ $? -eq 0 ]; then
    echo "✓ Multiple runs statistical analysis completed"
    echo "Experiment data saved to: $MULTI_RUN_DIR"
    
    # 创建多次运行信息文件
    INFO_FILE="$MULTI_RUN_DIR/multi_run_info.txt"
    echo "MicroBench Multiple Runs Experiment" > "$INFO_FILE"
    echo "======================================" >> "$INFO_FILE"
    echo "Date: $(date)" >> "$INFO_FILE"
    echo "Timestamp: $TIMESTAMP" >> "$INFO_FILE"
    echo "Total Runs: $NUM_RUNS" >> "$INFO_FILE"
    echo "Successful Runs: $SUCCESS_COUNT" >> "$INFO_FILE"
    echo "Sleep Between Runs: ${SLEEP_BETWEEN_RUNS}s" >> "$INFO_FILE"
    echo "Root Permissions: $HAVE_ROOT" >> "$INFO_FILE"
    echo >> "$INFO_FILE"
    echo "Individual Run Files:" >> "$INFO_FILE"
    for file in "${RESULT_FILES[@]}"; do
        echo "  - $(basename "$file")" >> "$INFO_FILE"
    done
else
    echo "✗ Statistical analysis failed"
    exit 1
fi

# 8. 恢复系统设置（如果修改了）
if [ "$HAVE_ROOT" = true ]; then
    echo
    echo "Restoring system settings..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo powersave > "$cpu" 2>/dev/null
    done
    echo "✓ CPU frequency strategy has been restored to powersave"
fi

# echo
# echo "=== 多次运行受控测试建议 ==="
# echo "1. 已完成 $SUCCESS_COUNT 次运行，获得了统计显著的数据"
# echo "2. 使用sudo运行以获得最佳控制效果: sudo $0"
# echo "3. 确保测试期间系统负载最小"
# echo "4. 可使用 -n 参数调整运行次数: $0 -n 50"
# echo "5. 可使用 -s 参数调整运行间隔: $0 -s 10"
# echo "6. 查看统计结果: $MULTI_RUN_DIR"
