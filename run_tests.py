#!/usr/bin/env python3
"""
Test runner script for Explicto-Nummus.
"""
import subprocess
import sys
import os


def run_tests():
    """Run all tests with coverage."""
    print("🧪 Running Explicto-Nummus Test Suite")
    print("=" * 50)
    
    # Run pytest with coverage
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/",
        "-v",
        "--cov=database",
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "--tb=short"
    ]
    
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ All tests passed!")
        print("📊 Coverage report generated in htmlcov/index.html")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


def run_unit_tests():
    """Run only unit tests."""
    print("🧪 Running Unit Tests")
    print("=" * 30)
    
    cmd = [sys.executable, "-m", "pytest", "tests/test_database.py", "tests/test_csv_parsing.py", "-v"]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Unit tests passed!")
    else:
        print("\n❌ Unit tests failed!")
        sys.exit(1)


def run_integration_tests():
    """Run only integration tests."""
    print("🧪 Running Integration Tests")
    print("=" * 35)
    
    cmd = [sys.executable, "-m", "pytest", "tests/test_integration.py", "-v"]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n✅ Integration tests passed!")
    else:
        print("\n❌ Integration tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            run_unit_tests()
        elif sys.argv[1] == "integration":
            run_integration_tests()
        else:
            print("Usage: python run_tests.py [unit|integration]")
            sys.exit(1)
    else:
        run_tests()
