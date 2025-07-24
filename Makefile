# Hippodrome Solver Makefile

CXX = g++
CXXFLAGS = -std=c++17 -O3 -pthread -Wall -Wextra
TARGET = solver
SOURCE = hippodrome_solver_working.cpp

# Default target
all: $(TARGET)

# Build the solver
$(TARGET): $(SOURCE)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SOURCE)

# Clean build artifacts
clean:
	rm -f $(TARGET) $(TARGET).exe *.o

# Install dependencies (for frontend)
install-deps:
	cd frontend_explorer && pip install -r requirements.txt

# Run tests
test:
	cd tests && python -m pytest

# Quick test with first 10 configurations
test-solver: $(TARGET)
	./$(TARGET) filtered_hippodrome_configs.csv test_output.csv 0-9 1

# Build and test
check: $(TARGET) test-solver test

# Help
help:
	@echo "Available targets:"
	@echo "  all          - Build the solver (default)"
	@echo "  clean        - Remove build artifacts"
	@echo "  install-deps - Install Python dependencies"
	@echo "  test         - Run Python unit tests"
	@echo "  test-solver  - Test solver with first 10 configs"
	@echo "  check        - Build and run all tests"
	@echo "  help         - Show this help message"

.PHONY: all clean install-deps test test-solver check help 