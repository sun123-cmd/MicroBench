# MicroBench Makefile
# Real-time Determinism CPU Benchmark

# Compiler and flags
CC = gcc
CFLAGS = -O2 -Wall -Wextra -std=c99 -march=native
LDFLAGS = -lm

# Directories
SRCDIR = .
BINDIR = ../bin

# Target executable
TARGET = $(BINDIR)/microbench

# Source files
COMMON_SRC = common.c
TEST_SRCS = test_pure_computation.c \
			test_regular_branches.c \
			test_pseudo_random_branches.c \
			test_nested_branches.c \
			test_memory_branch_mixed.c \
			test_high_frequency_branches.c
MAIN_SRC = microbench_main.c
ORIGINAL_SRC = microbench.c

# Object files
COMMON_OBJ = $(COMMON_SRC:.c=.o)
TEST_OBJS = $(TEST_SRCS:.c=.o)
MAIN_OBJ = $(MAIN_SRC:.c=.o)
ALL_OBJS = $(COMMON_OBJ) $(TEST_OBJS) $(MAIN_OBJ)

# Default target and phony targets
.PHONY: all clean clean-obj help install original both debug

# Mark object files as intermediate (can be deleted after use)
.INTERMEDIATE: $(ALL_OBJS)

all: $(TARGET)

# Create bin directory if it doesn't exist
$(BINDIR):
	mkdir -p $(BINDIR)

# Main target - modular version
$(TARGET): $(BINDIR) $(ALL_OBJS)
	@echo "Linking final executable..."
	$(CC) $(CFLAGS) $(ALL_OBJS) -o $@ $(LDFLAGS)
	@echo "Cleaning intermediate files..."
	@rm -f *.o
	@echo "Build completed successfully!"
	@echo "Generated executable: $@"

# Object file rules
%.o: %.c common.h
	@echo "Compiling $<..."
	$(CC) $(CFLAGS) -c $< -o $@

# Original monolithic version (if available)
original: $(BINDIR)
	@if [ -f $(ORIGINAL_SRC) ]; then \
		echo "Building original monolithic version..."; \
		$(CC) $(CFLAGS) $(ORIGINAL_SRC) -o $(BINDIR)/microbench $(LDFLAGS); \
		echo "Original version built: $(BINDIR)/microbench"; \
	else \
		echo "Note: $(ORIGINAL_SRC) not found, skipping original build"; \
	fi

# Both versions
both: all original

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f *.o
	rm -f $(BINDIR)/microbench $(BINDIR)/microbench_original
	@echo "Clean completed."

# Install (copy to system path - optional)
install: $(TARGET)
	@echo "Installing microbench to /usr/local/bin (requires sudo)..."
	sudo cp $(TARGET) /usr/local/bin/
	@echo "Installation completed."

# Help target
help:
	@echo "MicroBench Makefile Commands:"
	@echo ""
	@echo "  make          - Build modular version (default)"
	@echo "  make all      - Same as make"
	@echo "  make original - Build original version (if source available)"
	@echo "  make both     - Build both versions"
	@echo "  make clean    - Remove all build artifacts"
	@echo "  make clean-obj - Remove only object files"
	@echo "  make install  - Install to system (requires sudo)"
	@echo "  make help     - Show this help message"
	@echo "  make debug    - Show build variables"
	@echo ""
	@echo "Generated files:"
	@echo "  $(TARGET) - Modular version (recommended)"
	@echo "  $(BINDIR)/microbench_original - Original version (if built)"
	@echo ""
	@echo "Usage after build:"
	@echo "  cd $(BINDIR) && ./microbench > results.txt"
	@echo ""
	@echo "For analysis:"
	@echo "  cd ../tools && python3 analyze_results.py ../bin/results.txt"

# Declare dependencies
$(COMMON_OBJ): common.h
$(TEST_OBJS): common.h
$(MAIN_OBJ): common.h

# Debug target to show variables
debug:
	@echo "CC: $(CC)"
	@echo "CFLAGS: $(CFLAGS)"
	@echo "LDFLAGS: $(LDFLAGS)"
	@echo "TARGET: $(TARGET)"
	@echo "ALL_OBJS: $(ALL_OBJS)"
