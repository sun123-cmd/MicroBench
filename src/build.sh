#!/bin/bash

echo "Compile microbench for cross-platform..."

# 检测架构并设置编译选项
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

# 基础编译选项
CFLAGS="-O2 -pthread -std=c99"
LDFLAGS="-lm"

# 根据架构添加特定选项
case "$ARCH" in
    x86_64|i386|i686)
        echo "Compiling for x86 architecture"
        CFLAGS="$CFLAGS -march=native"
        ;;
    aarch64|arm64)
        echo "Compiling for ARM64 architecture"
        CFLAGS="$CFLAGS -mcpu=native"
        ;;
    arm*)
        echo "Compiling for ARM32 architecture"
        CFLAGS="$CFLAGS -mcpu=native"
        ;;
    *)
        echo "Compiling for generic architecture: $ARCH"
        ;;
esac

# 添加时间库链接
LDFLAGS="$LDFLAGS -lrt"

echo "Compile flags: $CFLAGS"
echo "Linker flags: $LDFLAGS"

gcc $CFLAGS microbench.c $LDFLAGS -o ../bin/microbench

if [ $? -eq 0 ]; then
    echo "✓ Compile Success, Output File: ../bin/microbench"
    echo "✓ Cross-platform timing support enabled"
    
    # 显示编译信息
    echo
    echo "Binary info:"
    file ../bin/microbench 2>/dev/null || echo "file command not available"
else
    echo "✗ Compile Failed"
    echo
    echo "Troubleshooting tips:"
    echo "1. Make sure gcc is installed"
    echo "2. On some systems, use 'clang' instead of 'gcc'"
    echo "3. Try: apt-get install build-essential (Ubuntu/Debian)"
    echo "4. Try: yum install gcc (CentOS/RHEL)"
    exit 1
fi
