#!/usr/bin/env python3
"""Simple script to test ruff installation and run checks."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n🔍 {description}")
    print(f"Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=Path.cwd())

        if result.returncode == 0:
            print("✅ Success!")
            if result.stdout:
                print(f"Output:\n{result.stdout}")
        else:
            print("❌ Failed!")
            if result.stderr:
                print(f"Error:\n{result.stderr}")
            if result.stdout:
                print(f"Output:\n{result.stdout}")

        return result.returncode == 0
    except FileNotFoundError:
        print(f"❌ Command not found: {cmd[0]}")
        return False
    except Exception as e:
        print(f"❌ Error running command: {e}")
        return False


def main():
    """Run ruff checks."""
    print("🚀 Running Code Quality Checks")

    # Check if ruff is installed
    if not run_command([sys.executable, "-m", "ruff", "--version"], "Checking ruff installation"):
        print("\n📦 Installing ruff...")
        if not run_command([sys.executable, "-m", "pip", "install", "ruff"], "Installing ruff"):
            print("Failed to install ruff")
            return False

    # Run linting
    run_command([sys.executable, "-m", "ruff", "check", "."], "Running ruff linting")

    # Run formatting check
    run_command(
        [sys.executable, "-m", "ruff", "format", "--check", "."], "Running ruff formatting check"
    )

    print("\n🎉 Code quality checks completed!")


if __name__ == "__main__":
    main()
