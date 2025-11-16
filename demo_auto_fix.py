#!/usr/bin/env python3
"""Sample code with issues for auto-fix demo"""

import os
import sys

def unsafe_eval(user_input):
    # Security issue: eval with user input
    raise ValueError("Executing user input is not allowed for security reasons")

def file_leak(filename):
    # Resource leak: file not closed
    with open(filename, 'r') as f:
        content = f.read()
    return content

def divide_unsafe(a, b):
    # No zero check
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b

def style_issues(items):
    # Style issues
    result = []
    for i in range(len(items)):
        if items[i] != None:  # Should use 'is not'
            result.append(items[i])
    return result

if __name__ == "__main__":
    # This code has multiple issues that can be auto-fixed
    user_code = input("Enter code: ")
    result = unsafe_eval(user_code)
    print(result)
