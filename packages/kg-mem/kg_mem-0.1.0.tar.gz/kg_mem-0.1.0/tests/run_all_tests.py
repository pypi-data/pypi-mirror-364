#!/usr/bin/env python3
"""
Run all KGMem tests.
This script runs all test files in the tests directory.
"""

import sys
import pytest
from pathlib import Path

def main():
    """Run all tests in the current directory."""
    # Get the tests directory
    tests_dir = Path(__file__).parent
    
    # Run pytest on all test_*.py files
    print("Running all KGMem tests...")
    print("-" * 50)
    
    # Run tests with verbose output
    exit_code = pytest.main([
        str(tests_dir),
        "-v",  # Verbose
        "--tb=short",  # Short traceback format
        "-x",  # Stop on first failure
        "--color=yes",  # Colored output
    ])
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n❌ Tests failed with exit code: {exit_code}")
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 