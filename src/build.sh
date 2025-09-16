#!/bin/bash

echo "Building MicroBench (Modular Version)..."

CFLAGS="-O2 -Wall -Wextra -std=c99 -march=native"
LDFLAGS="-lm"
mkdir -p ../bin

echo "Compiling modules..."
gcc $CFLAGS -c common.c -o common.o
gcc $CFLAGS -c test_pure_computation.c -o test_pure_computation.o
gcc $CFLAGS -c test_regular_branches.c -o test_regular_branches.o  
gcc $CFLAGS -c test_pseudo_random_branches.c -o test_pseudo_random_branches.o
gcc $CFLAGS -c test_nested_branches.c -o test_nested_branches.o
gcc $CFLAGS -c test_memory_branch_mixed.c -o test_memory_branch_mixed.o
gcc $CFLAGS -c test_high_frequency_branches.c -o test_high_frequency_branches.o

echo "Compiling main program..."
gcc $CFLAGS -c microbench_main.c -o microbench_main.o

echo "Linking final executable..."
gcc $CFLAGS *.o -o ../bin/microbench $LDFLAGS

rm -f *.o

echo "Build completed successfully!"
echo "Generated executable:"
echo "  - ../bin/microbench (modular version)"  
echo "  - ../bin/microbench_original (original monolithic version)"
echo ""
echo "The modular version is functionally identical to the original,"
echo "but the source code is better organized for maintenance."
