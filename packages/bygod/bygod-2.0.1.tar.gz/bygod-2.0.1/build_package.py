#!/usr/bin/env python3
"""
Build script for bygod package
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Error: {e.stderr}")
        sys.exit(1)

def main():
    """Main build process."""
    print("🚀 Starting bygod package build process...")
    
    # Clean previous builds
    print("🧹 Cleaning previous builds...")
    for path in ["build", "dist", "*.egg-info"]:
        run_command(f"rm -rf {path}", f"Cleaning {path}")
    
    # Install build dependencies
    print("📦 Installing build dependencies...")
    run_command("pip install --upgrade build twine", "Installing build tools")
    
    # Build the package
    print("🔨 Building package...")
    run_command("python -m build", "Building package")
    
    # Check the built package
    print("🔍 Checking built package...")
    run_command("twine check dist/*", "Checking package")
    
    # List built files
    print("📋 Built files:")
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.glob("*"):
            print(f"   📄 {file}")
    
    print("\n🎉 Package build completed successfully!")
    print("\n📤 To upload to PyPI (TestPyPI first):")
    print("   twine upload --repository testpypi dist/*")
    print("\n📤 To upload to PyPI (production):")
    print("   twine upload dist/*")
    print("\n🧪 To test installation locally:")
    print("   pip install dist/bygod-*.whl")

if __name__ == "__main__":
    main() 