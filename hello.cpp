#include <iostream>
#include <string>

int main() {
    std::cout << "Hello, World!" << std::endl;
    std::cout << "Welcome to C++ programming!" << std::endl;
    
    // Test some basic C++ features
    std::string name;
    std::cout << "Enter your name: ";
    std::getline(std::cin, name);
    std::cout << "Hello, " << name << "! Ready to start coding C++?" << std::endl;
    
    return 0;
}
