#include <iostream>
#include <string>
#include <iomanip>

int main() {
    std::cout << "=== C++ Lesson 1: Variables and Data Types ===" << std::endl;
    std::cout << std::endl;

    // 1. INTEGER TYPES
    std::cout << "1. INTEGER TYPES:" << std::endl;
    int age = 25;                    // Most common integer type
    short smallNumber = 100;         // Smaller range, uses less memory
    long largeNumber = 1000000L;     // Larger range
    long long veryLarge = 123456789012345LL; // Even larger range
    
    std::cout << "int age = " << age << std::endl;
    std::cout << "short smallNumber = " << smallNumber << std::endl;
    std::cout << "long largeNumber = " << largeNumber << std::endl;
    std::cout << "long long veryLarge = " << veryLarge << std::endl;
    std::cout << std::endl;

    // 2. FLOATING POINT TYPES
    std::cout << "2. FLOATING POINT TYPES:" << std::endl;
    float price = 19.99f;            // Single precision (7 decimal digits)
    double distance = 384400.5;      // Double precision (15 decimal digits)
    long double precise = 3.14159265358979323846L; // Extended precision
    
    std::cout << std::fixed << std::setprecision(2);
    std::cout << "float price = $" << price << std::endl;
    std::cout << "double distance = " << distance << " km" << std::endl;
    std::cout << std::setprecision(10);
    std::cout << "long double precise = " << precise << std::endl;
    std::cout << std::endl;

    // 3. CHARACTER TYPE
    std::cout << "3. CHARACTER TYPE:" << std::endl;
    char grade = 'A';                // Single character (uses single quotes)
    char symbol = '$';
    
    std::cout << "char grade = '" << grade << "'" << std::endl;
    std::cout << "char symbol = '" << symbol << "'" << std::endl;
    std::cout << std::endl;

    // 4. BOOLEAN TYPE
    std::cout << "4. BOOLEAN TYPE:" << std::endl;
    bool isStudent = true;           // Can be true or false
    bool hasLicense = false;
    
    std::cout << std::boolalpha;     // Print true/false instead of 1/0
    std::cout << "bool isStudent = " << isStudent << std::endl;
    std::cout << "bool hasLicense = " << hasLicense << std::endl;
    std::cout << std::endl;

    // 5. STRING TYPE
    std::cout << "5. STRING TYPE:" << std::endl;
    std::string firstName = "John";  // C++ string class (uses double quotes)
    std::string lastName = "Doe";
    std::string fullName = firstName + " " + lastName; // String concatenation
    
    std::cout << "std::string firstName = \"" << firstName << "\"" << std::endl;
    std::cout << "std::string lastName = \"" << lastName << "\"" << std::endl;
    std::cout << "std::string fullName = \"" << fullName << "\"" << std::endl;
    std::cout << "String length: " << fullName.length() << " characters" << std::endl;
    std::cout << std::endl;

    // 6. CONSTANTS
    std::cout << "6. CONSTANTS:" << std::endl;
    const double PI = 3.14159;       // Cannot be changed after initialization
    const int DAYS_IN_WEEK = 7;
    
    std::cout << "const double PI = " << PI << std::endl;
    std::cout << "const int DAYS_IN_WEEK = " << DAYS_IN_WEEK << std::endl;
    std::cout << std::endl;

    // 7. AUTO KEYWORD (C++11 and later)
    std::cout << "7. AUTO KEYWORD (Modern C++):" << std::endl;
    auto autoInt = 42;              // Compiler deduces this is int
    auto autoDouble = 3.14;         // Compiler deduces this is double
    auto autoString = std::string("Hello"); // Compiler deduces this is string
    
    std::cout << "auto autoInt = " << autoInt << " (type: int)" << std::endl;
    std::cout << "auto autoDouble = " << autoDouble << " (type: double)" << std::endl;
    std::cout << "auto autoString = \"" << autoString << "\" (type: string)" << std::endl;
    std::cout << std::endl;

    // 8. VARIABLE SCOPE EXAMPLE
    std::cout << "8. VARIABLE SCOPE:" << std::endl;
    int globalVar = 100;
    {
        int localVar = 200;          // Only exists within these braces
        std::cout << "Inside block - globalVar: " << globalVar << std::endl;
        std::cout << "Inside block - localVar: " << localVar << std::endl;
    }
    // localVar is no longer accessible here
    std::cout << "Outside block - globalVar: " << globalVar << std::endl;
    std::cout << std::endl;

    std::cout << "🎉 Lesson 1 Complete! Try modifying the values and recompiling." << std::endl;
    
    return 0;
}
