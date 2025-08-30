# C++ Development Environment - Getting Started

## 🎉 Setup Complete!

Your C++ development environment is now ready! Here's what was installed:

### Installed Components
- **MSYS2**: Unix-like environment for Windows
- **GCC/G++ 15.1.0**: Modern C++ compiler with C++17/20 support
- **GDB**: Debugger for C++ programs
- **Make**: Build automation tool
- **VS Code Extensions**: C++ IntelliSense and debugging support

### Basic Commands

#### Compilation
```bash
# Compile a single file
g++ -o program.exe source.cpp

# Compile with modern C++ standard and warnings
g++ -std=c++17 -Wall -Wextra -g -o program.exe source.cpp

# Using the Makefile
make all        # Build the program
make clean      # Clean build artifacts
make run        # Build and run
make help       # Show available targets
```

#### Running Programs
```bash
# Run the compiled executable
./program.exe
```

### VS Code Integration

#### Building (Ctrl+Shift+P)
1. Open Command Palette: `Ctrl+Shift+P`
2. Type: "Tasks: Run Task"
3. Select: "C/C++: g++ build active file"

#### Debugging (F5)
1. Open a C++ file
2. Press `F5` to start debugging
3. Set breakpoints by clicking in the gutter

### Your First Program

I've created `hello.cpp` as a starter program. Try these commands:

```bash
# Compile and run manually
g++ -o hello.exe hello.cpp
./hello.exe

# Or use make
make clean
make run
```

### Next Steps

1. **Learn C++ Basics**: Start with variables, loops, and functions
2. **Practice**: Try coding challenges on HackerRank or LeetCode
3. **Projects**: Build simple programs like calculators or text games
4. **Advanced**: Explore STL containers, classes, and modern C++ features

### Useful Resources
- [cppreference.com](https://cppreference.com) - Best C++ reference
- [learncpp.com](https://learncpp.com) - Excellent tutorials
- [C++ Core Guidelines](https://isocpp.github.io/CppCoreGuidelines/) - Best practices

### Troubleshooting

If gcc/g++ commands are not found in a new terminal session:
1. Close and reopen your terminal
2. Or manually add to PATH: `$env:PATH += ";C:\msys64\ucrt64\bin;C:\msys64\usr\bin"`

Happy coding! 🚀
