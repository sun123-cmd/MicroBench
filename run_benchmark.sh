#!/bin/bash
# MicroBench 主运行脚本 - 从根目录启动

echo "=== MicroBench Real-time Benchmark Tool ==="


# 检查目录结构
for dir in src bin tools result; do
    if [ ! -d "$dir" ]; then
        echo "Error: missing directory $dir"
        exit 1
    fi
done

# 检查是否需要编译
if [ ! -f "bin/microbench" ] || [ "src/microbench.c" -nt "bin/microbench" ]; then
    echo "Step 0: Compile program..."
    cd src
    bash build.sh
    if [ $? -ne 0 ]; then
        echo "✗ Compile failed"
        exit 1
    fi
    cd ..
fi

# 运行分析
echo "Step 1: Start real-time analysis..."
cd tools
bash run_analysis.sh
exit_code=$?
cd ..

if [ $exit_code -eq 0 ]; then
    echo
    echo "=== Analysis completed ==="
    echo "View result files:"
    echo "  cd result/ && ls -lt"
else
    echo "✗ Analysis process failed"
    exit 1
fi
