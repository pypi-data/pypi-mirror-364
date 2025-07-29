"""
Math

This module is some tools related to the math.
"""

def add(num1, num2):
    """
    Sum of two numbers.
    Input two number and get their summation.
    """
    return num1 + num2

def subtract(num1, num2):
    """
    Find the difference between two numbers.
    Input two number and get their difference.
    """
    return num1 - num2

def fibonacci_number(n):
    """
    Obtain the value of the nth number of Fibonacci sequence.
    """
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a