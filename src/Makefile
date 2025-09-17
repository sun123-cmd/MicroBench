# MicroBench Makefile
# Real-time Determinism CPU Benchmark

# Compiler and flags
CC = gcc
CFLAGS = -O2 -Wall -Wextra -std=c99 -march=native
LDFLAGS = -lm

# Directories
SRCDIR = .
BINDIR = ../bin

# Target executables
TARGET_ALL = $(BINDIR)/microbench
TARGET_INDIVIDUAL = $(addprefix $(BINDIR)/, $(basename $(TEST_SRCS)))

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
.PHONY: all all-in-one individual clean clean-obj help install original both debug

# Mark object files as intermediate (can be deleted after use)
.INTERMEDIATE: $(ALL_OBJS)

# Default target - build all-in-one version
all: all-in-one

# Create bin directory if it doesn't exist
$(BINDIR):
	mkdir -p $(BINDIR)

# All-in-one version - single executable with all test cases
all-in-one: $(TARGET_ALL)

$(TARGET_ALL): $(BINDIR) $(ALL_OBJS)
	@echo "Linking all-in-one executable..."
	$(CC) $(CFLAGS) $(ALL_OBJS) -o $@ $(LDFLAGS)
	@echo "Cleaning intermediate files..."
	@rm -f *.o
	@echo "All-in-one build completed successfully!"
	@echo "Generated executable: $@"

# Individual version - separate executable for each test case
individual: $(TARGET_INDIVIDUAL)

# Rule to build individual test executables
$(BINDIR)/%: %.c $(COMMON_SRC) common.h $(BINDIR)
	@echo "Building individual test: $*..."
	@echo "#include \"common.h\"" > temp_$*_main.c
	@echo "#include <stdio.h>" >> temp_$*_main.c
	@echo "#include <stdlib.h>" >> temp_$*_main.c
	@echo "" >> temp_$*_main.c
	@echo "// External test function declaration" >> temp_$*_main.c
	@grep "void.*$*" $< | sed 's/void \([^(]*\).*$$/extern void \1();/' >> temp_$*_main.c
	@echo "" >> temp_$*_main.c
	@echo "int main() {" >> temp_$*_main.c
	@echo "    printf(\"MicroBench - Individual Test: $*\\n\");" >> temp_$*_main.c
	@echo "    printf(\"===================================\\n\");" >> temp_$*_main.c
	@grep "void.*$*" $< | sed 's/void \([^(]*\).*$$/    \1();/' >> temp_$*_main.c
	@echo "    return 0;" >> temp_$*_main.c
	@echo "}" >> temp_$*_main.c
	$(CC) $(CFLAGS) $(COMMON_SRC) $< temp_$*_main.c -o $@ $(LDFLAGS)
	@rm -f temp_$*_main.c
	@echo "Individual test built: $@"

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

# Both compilation modes
both: all-in-one individual

# Build everything including original if available
all-targets: all-in-one individual original

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	rm -f *.o temp_*_main.c
	rm -f $(BINDIR)/microbench $(BINDIR)/microbench_original
	rm -f $(TARGET_INDIVIDUAL)
	@echo "Clean completed."

# Install (copy to system path - optional)
install: $(TARGET_ALL)
	@echo "Installing microbench to /usr/local/bin (requires sudo)..."
	sudo cp $(TARGET_ALL) /usr/local/bin/
	@echo "Installation completed."

# Help target
help:
	@echo "MicroBench Makefile Commands:"
	@echo ""
	@echo "=== Compile Options ==="
	@echo "  make             - Default (all-in-one mode)"
	@echo "  make all-in-one  - Build single executable (contains all test cases)"
	@echo "  make individual  - Build individual executables (one for each test)"
	@echo "  make both        - Build both modes"
	@echo "  make original    - Build original single file version (if source available)"
	@echo "  make all-targets - Build all versions"
	@echo ""
	@echo "=== Clean and Maintenance ==="
	@echo "  make clean       - Clean all build artifacts"
	@echo "  make clean-obj   - Clean only object files"
	@echo "  make install     - Install to system path (requires sudo)"
	@echo "  make help        - Show this help message"
	@echo "  make debug       - Show build variables"
	@echo ""
	@echo "=== Generated Files ==="
	@echo "  $(TARGET_ALL) - Single executable (recommended)"
	@echo "  $(BINDIR)/test_* - Individual test executables"
	@echo "  $(BINDIR)/microbench_original - Original version (if built)"

# Declare dependencies
$(COMMON_OBJ): common.h
$(TEST_OBJS): common.h
$(MAIN_OBJ): common.h

# Debug target to show variables
debug:
	@echo "CC: $(CC)"
	@echo "CFLAGS: $(CFLAGS)"
	@echo "LDFLAGS: $(LDFLAGS)"
	@echo "TARGET_ALL: $(TARGET_ALL)"
	@echo "TARGET_INDIVIDUAL: $(TARGET_INDIVIDUAL)"
	@echo "ALL_OBJS: $(ALL_OBJS)"
	@echo "TEST_SRCS: $(TEST_SRCS)"
