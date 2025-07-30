#!/usr/bin/env python3
"""
🧪 School of Prompt Test Runner

Simple script to run the test suite with coverage reporting.
"""

import os
import subprocess
import sys


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔍 {description}")
    print(f"Running: {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"❌ {description} failed!")
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return False
    else:
        print(f"✅ {description} passed!")
        if result.stdout:
            print(result.stdout)
        return True


def main():
    """Run the complete test suite."""
    print("🎸 School of Prompt Test Suite")
    print("=" * 50)

    # Check if we're in the right directory
    if not os.path.exists("school_of_prompt"):
        print("❌ Please run this script from the project root directory")
        sys.exit(1)

    # Install dependencies if needed
    print("📦 Installing test dependencies...")
    subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "pytest",
            "pytest-cov",
            "black",
            "isort",
            "flake8",
        ],
        check=True,
    )

    success = True

    # Run code formatting check
    success &= run_command(
        ["black", "--check", "--diff", "school_of_prompt/", "examples/", "tests/"],
        "Code formatting check",
    )

    # Run import sorting check
    success &= run_command(
        ["isort", "--check-only", "--diff", "school_of_prompt/", "examples/", "tests/"],
        "Import sorting check",
    )

    # Run linting
    success &= run_command(
        [
            "flake8",
            "school_of_prompt/",
            "examples/",
            "tests/",
            "--max-line-length=88",
            "--extend-ignore=E203,W503",
        ],
        "Code linting",
    )

    # Run tests with coverage
    success &= run_command(
        [
            "pytest",
            "tests/",
            "--cov=school_of_prompt",
            "--cov-report=term-missing",
            "--cov-report=html",
            "-v",
        ],
        "Unit tests with coverage",
    )

    print("\n" + "=" * 50)
    if success:
        print("🎉 All tests passed! Ready to rock! 🎸")
        print("📊 Coverage report saved to htmlcov/index.html")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
