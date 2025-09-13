#!/bin/bash

echo "Compile microbench for cross-platform..."

# 检测系统和架构
OS=$(uname -s)
ARCH=$(uname -m)
echo "Detected OS: $OS"
echo "Detected architecture: $ARCH"

# 基础编译选项
CFLAGS="-O2 -pthread -std=c99"
LDFLAGS="-lm"

# 根据操作系统设置链接选项
case "$OS" in
    Linux)
        echo "Compiling for Linux"
        LDFLAGS="$LDFLAGS -lrt"
        ;;
    Darwin)
        echo "Compiling for macOS"
        # macOS不需要-lrt，clock_gettime已包含在系统库中
        ;;
    FreeBSD|OpenBSD|NetBSD)
        echo "Compiling for BSD"
        # BSD系统通常不需要-lrt
        ;;
    *)
        echo "Compiling for unknown OS: $OS"
        echo "Trying without -lrt first..."
        ;;
esac

# 根据架构添加特定选项
case "$ARCH" in
    x86_64|i386|i686)
        echo "Compiling for x86 architecture"
        if [ "$OS" = "Darwin" ]; then
            # macOS上使用不同的优化选项
            CFLAGS="$CFLAGS -march=native"
        else
            CFLAGS="$CFLAGS -march=native"
        fi
        ;;
    aarch64|arm64)
        echo "Compiling for ARM64 architecture"
        if [ "$OS" = "Darwin" ]; then
            # macOS ARM64 - 使用通用优化，避免特定CPU型号
            CFLAGS="$CFLAGS -march=armv8-a"
        else
            # Linux ARM64
            CFLAGS="$CFLAGS -mcpu=native"
        fi
        ;;
    arm*)
        echo "Compiling for ARM32 architecture"
        CFLAGS="$CFLAGS -mcpu=native"
        ;;
    *)
        echo "Compiling for generic architecture: $ARCH"
        ;;
esac

# 选择编译器
if [ "$OS" = "Darwin" ]; then
    # macOS 默认使用clang
    COMPILER="clang"
else
    # Linux等使用gcc
    COMPILER="gcc"
fi

echo "Using compiler: $COMPILER"
echo "Compile flags: $CFLAGS"
echo "Linker flags: $LDFLAGS"

# 尝试编译
$COMPILER $CFLAGS microbench.c $LDFLAGS -o ../bin/microbench

if [ $? -eq 0 ]; then
    echo "✓ Compile Success, Output File: ../bin/microbench"
    echo "✓ Cross-platform timing support enabled"
    
    # 显示编译信息
    echo
    echo "Binary info:"
    file ../bin/microbench 2>/dev/null || echo "file command not available"
    
    # 显示依赖库信息
    echo "Dependencies:"
    if [ "$OS" = "Darwin" ]; then
        otool -L ../bin/microbench 2>/dev/null || echo "otool not available"
    else
        ldd ../bin/microbench 2>/dev/null || echo "ldd not available"
    fi
else
    echo "✗ Compile Failed"
    echo
    echo "Troubleshooting tips for $OS:"
    if [ "$OS" = "Darwin" ]; then
        echo "1. Install Xcode Command Line Tools: xcode-select --install"
        echo "2. Make sure clang is available: which clang"
        echo "3. Check macOS version compatibility"
    else
        echo "1. Make sure gcc is installed"
        echo "2. Try: apt-get install build-essential (Ubuntu/Debian)"
        echo "3. Try: yum install gcc (CentOS/RHEL)"
        echo "4. Alternative: use clang if gcc not available"
    fi
    exit 1
fi
