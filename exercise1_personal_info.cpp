#include <iostream>
#include <string>

int main() {
    std::cout << "=== Exercise 1: Personal Information Program ===" << std::endl;
    std::cout << "Fill in your own information by modifying the variables below:" << std::endl;
    std::cout << std::endl;

    // TODO: Replace these with your own information
    std::string name = "Your Name Here";
    int age = 0;                    // Your age
    double height = 0.0;            // Your height in meters (e.g., 1.75)
    char grade = 'A';               // A grade you're proud of
    bool isLearning = true;         // Are you learning C++?
    std::string hobby = "Your favorite hobby";
    const std::string COUNTRY = "Your Country"; // This won't change
    
    // Calculate some derived information
    int birthYear = 2025 - age;     // Approximate birth year
    double heightInCm = height * 100; // Convert to centimeters
    
    // Display the information
    std::cout << "📋 Personal Information:" << std::endl;
    std::cout << "Name: " << name << std::endl;
    std::cout << "Age: " << age << " years old" << std::endl;
    std::cout << "Approximate birth year: " << birthYear << std::endl;
    std::cout << "Height: " << height << "m (" << heightInCm << "cm)" << std::endl;
    std::cout << "Favorite grade: " << grade << std::endl;
    std::cout << "Currently learning C++: " << (isLearning ? "Yes!" : "No") << std::endl;
    std::cout << "Favorite hobby: " << hobby << std::endl;
    std::cout << "Country: " << COUNTRY << std::endl;
    std::cout << std::endl;
    
    // Fun calculations
    std::cout << "🔢 Fun Calculations:" << std::endl;
    std::cout << "Days lived (approximately): " << (age * 365) << " days" << std::endl;
    std::cout << "Height in inches (approximately): " << (height * 39.37) << " inches" << std::endl;
    std::cout << "Name length: " << name.length() << " characters" << std::endl;
    
    std::cout << std::endl;
    std::cout << "✅ Exercise 1 complete! Great job practicing with variables!" << std::endl;
    
    return 0;
}
