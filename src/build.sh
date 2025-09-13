#!/bin/bash


echo "Compile microbench..."
gcc -O2 -pthread microbench.c -lm -o ../bin/microbench

if [ $? -eq 0 ]; then
    echo "✓ Compile Success, Output File: ../bin/microbench"
else
    echo "✗ Combile Failed"
    exit 1
fi
