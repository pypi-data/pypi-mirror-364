#!/usr/bin/env python3
"""
Release script for bygod package
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
        return None

def main():
    """Main release process."""
    print("🚀 Starting bygod package release process...")
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("❌ Not in a git repository. Please run this from the project root.")
        sys.exit(1)
    
    # Check if there are uncommitted changes
    result = subprocess.run("git status --porcelain", shell=True, capture_output=True, text=True)
    if result.stdout.strip():
        print("❌ There are uncommitted changes. Please commit or stash them first.")
        print("   Changes:")
        print(result.stdout)
        sys.exit(1)
    
    # Build the package
    print("🔨 Building package...")
    if not run_command("python build_package.py", "Building package"):
        sys.exit(1)
    
    # Check if dist directory exists and has files
    dist_dir = Path("dist")
    if not dist_dir.exists() or not list(dist_dir.glob("*")):
        print("❌ No built packages found in dist/ directory")
        sys.exit(1)
    
    # List built files
    print("📋 Built files:")
    for file in dist_dir.glob("*"):
        print(f"   📄 {file}")
    
    # Ask user what to do
    print("\n🎯 Release Options:")
    print("1. Upload to TestPyPI (recommended for testing)")
    print("2. Upload to PyPI (production)")
    print("3. Just build (no upload)")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n📤 Uploading to TestPyPI...")
        if not run_command("twine upload --repository testpypi dist/*", "Uploading to TestPyPI"):
            sys.exit(1)
        print("\n✅ Package uploaded to TestPyPI!")
        print("🔗 TestPyPI URL: https://test.pypi.org/project/bygod/")
        print("\n🧪 To test installation from TestPyPI:")
        print("   pip install --index-url https://test.pypi.org/simple/ bygod")
        
    elif choice == "2":
        print("\n⚠️  WARNING: This will upload to production PyPI!")
        confirm = input("Are you sure you want to upload to production PyPI? (yes/no): ").strip().lower()
        
        if confirm == "yes":
            print("\n📤 Uploading to PyPI...")
            if not run_command("twine upload dist/*", "Uploading to PyPI"):
                sys.exit(1)
            print("\n✅ Package uploaded to PyPI!")
            print("🔗 PyPI URL: https://pypi.org/project/bygod/")
            print("\n🎉 Users can now install with: pip install bygod")
        else:
            print("❌ Upload cancelled")
            
    elif choice == "3":
        print("\n✅ Package built successfully!")
        print("📦 Files are ready in the dist/ directory")
        
    else:
        print("❌ Invalid choice")
        sys.exit(1)
    
    print("\n🎉 Release process completed!")

if __name__ == "__main__":
    main() 