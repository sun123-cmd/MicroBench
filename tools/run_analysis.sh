#!/bin/bash
# MicroBench 实时性分析运行脚本

echo "=== MicroBench 实时性分析工具 ==="
echo

# 检查microbench是否存在
if [ ! -f "../bin/microbench" ]; then
    echo "Error: microbench executable file does not exist"
    echo "Please run: cd ../src && bash build.sh"
    exit 1
fi

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 environment is required"
    exit 1
fi

# 生成时间戳和临时结果文件
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
TEMP_RESULTS_FILE="../result/temp_benchmark_${TIMESTAMP}.txt"

echo "Step 1: Run microbench..."
echo "Output will be saved temporarily to: $TEMP_RESULTS_FILE"
../bin/microbench > "$TEMP_RESULTS_FILE"

if [ $? -eq 0 ]; then
    echo "✓ Benchmark test completed"
else
    echo "✗ Benchmark test failed"
    exit 1
fi

echo
echo "Step 2: Analyze real-time metrics and organize results..."
python3 analyze_results.py "$TEMP_RESULTS_FILE" -o "rt_analysis_${TIMESTAMP}.csv"

if [ $? -eq 0 ]; then
    # 清理临时文件
    rm -f "$TEMP_RESULTS_FILE"
    
    echo
    echo "=== Analysis completed ==="
    echo "All experimental data has been organized into timestamped directories"
    echo "Check ../result/experiment_* directories for complete results"
    
    # 显示最新的实验目录
    LATEST_EXP=$(ls -td ../result/experiment_* 2>/dev/null | head -1)
    if [ -n "$LATEST_EXP" ]; then
        echo
        echo "Latest experiment directory: $(basename "$LATEST_EXP")"
        echo "Contents:"
        ls -la "$LATEST_EXP" | grep -v '^d' | grep -v '^total' | sed 's/^/  /'
    fi
else
    echo "✗ Analysis failed"
    # 清理临时文件
    rm -f "$TEMP_RESULTS_FILE"
    exit 1
fi
