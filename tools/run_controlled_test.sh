#!/bin/bash
# 受控环境的微基准测试脚本

echo "=== MicroBench Stablized Test ==="
echo

# 检查是否以root权限运行
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

# 7. 运行基准测试
echo
echo "=== 开始受控基准测试 ==="

# 检查microbench是否存在
if [ ! -f "../bin/microbench" ]; then
    echo "错误: microbench可执行文件不存在"
    echo "请先运行: cd ../src && bash build.sh"
    exit 1
fi

# 生成时间戳和临时结果文件
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEMP_RESULTS_FILE="../result/temp_controlled_${TIMESTAMP}.txt"

echo "运行受控测试..."
echo "输出将保存到: $TEMP_RESULTS_FILE"

# 使用taskset确保在单核上运行
if command -v taskset >/dev/null 2>&1; then
    taskset -c 0 ../bin/microbench > "$TEMP_RESULTS_FILE"
else
    ../bin/microbench > "$TEMP_RESULTS_FILE"
fi

if [ $? -eq 0 ]; then
    echo "✓ 受控基准测试完成"
else
    echo "✗ 受控基准测试失败"
    exit 1
fi

echo
echo "=== 分析测试结果 ==="
python3 analyze_results.py "$TEMP_RESULTS_FILE" -o "controlled_analysis_${TIMESTAMP}.csv"

if [ $? -eq 0 ]; then
    # 清理临时文件
    rm -f "$TEMP_RESULTS_FILE"
    
    echo
    echo "=== 受控测试完成 ==="
    echo "实验数据已保存到timestamped目录"
    
    # 显示最新的实验目录
    LATEST_EXP=$(ls -td ../result/experiment_* 2>/dev/null | head -1)
    if [ -n "$LATEST_EXP" ]; then
        echo
        echo "最新实验目录: $(basename "$LATEST_EXP")"
        echo "包含受控环境测试结果"
    fi
else
    echo "✗ 分析失败"
    rm -f "$TEMP_RESULTS_FILE"
    exit 1
fi

# 8. 恢复系统设置（如果修改了）
if [ "$HAVE_ROOT" = true ]; then
    echo
    echo "恢复系统设置..."
    for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
        echo powersave > "$cpu" 2>/dev/null
    done
    echo "✓ CPU频率策略已恢复为powersave"
fi

echo
echo "=== 受控测试建议 ==="
echo "1. 多次运行此脚本以获得统计显著性"
echo "2. 使用sudo运行以获得最佳控制效果"
echo "3. 确保测试期间系统负载最小"
echo "4. 比较受控测试和普通测试的差异"
