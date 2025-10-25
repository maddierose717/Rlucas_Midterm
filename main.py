#!/usr/bin/env python3
"""Main entry point for the calculator application."""

from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from colorama import init, Fore, Style

def main():
    # Initialize colorama for cross-platform color support
    init(autoreset=True)
    
    print(Fore.CYAN + "="*50)
    print(Fore.CYAN + "Welcome to the Advanced Calculator")
    print(Fore.CYAN + "="*50)
    
    config = CalculatorConfig()
    calculator = Calculator(config)
    
    # Run the calculator's main loop
    calculator.run()

if __name__ == "__main__":
    main()
