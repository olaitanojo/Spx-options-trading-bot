# Simple Makefile for C++ projects
CXX = g++
CXXFLAGS = -std=c++17 -Wall -Wextra -g
TARGET = hello
SOURCES = hello.cpp

# Default target
all: $(TARGET)

# Build the main target
$(TARGET): $(SOURCES)
	$(CXX) $(CXXFLAGS) -o $(TARGET).exe $(SOURCES)

# Clean build artifacts
clean:
	rm -f *.exe *.o

# Run the program
run: $(TARGET)
	./$(TARGET).exe

# Help target
help:
	@echo "Available targets:"
	@echo "  all     - Build the program"
	@echo "  clean   - Remove build artifacts" 
	@echo "  run     - Build and run the program"
	@echo "  help    - Show this help message"

.PHONY: all clean run help
