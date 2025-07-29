#!/usr/bin/env python3
"""
Setup script for Bible Gateway Downloader - True Async Edition
"""

from setuptools import setup, find_packages
import os
import re

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from Pipfile
def read_pipfile_requirements():
    requirements = []
    if os.path.exists("Pipfile"):
        with open("Pipfile", "r", encoding="utf-8") as fh:
            content = fh.read()
            
        # Extract packages from [packages] section
        packages_match = re.search(r'\[packages\](.*?)(?=\[|$)', content, re.DOTALL)
        if packages_match:
            packages_section = packages_match.group(1)
            for line in packages_section.split('\n'):
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    # Parse package name and version
                    package_match = re.match(r'(\w+)\s*=\s*["\']?([^"\']*)["\']?', line)
                    if package_match:
                        package_name = package_match.group(1)
                        version_spec = package_match.group(2).strip()
                        if version_spec and version_spec != '*':
                            requirements.append(f"{package_name}{version_spec}")
                        else:
                            requirements.append(package_name)
    
    return requirements

# Read dev requirements from Pipfile
def read_pipfile_dev_requirements():
    requirements = []
    if os.path.exists("Pipfile"):
        with open("Pipfile", "r", encoding="utf-8") as fh:
            content = fh.read()
            
        # Extract packages from [dev-packages] section
        dev_packages_match = re.search(r'\[dev-packages\](.*?)(?=\[|$)', content, re.DOTALL)
        if dev_packages_match:
            dev_packages_section = dev_packages_match.group(1)
            for line in dev_packages_section.split('\n'):
                line = line.strip()
                if line and '=' in line and not line.startswith('#'):
                    # Parse package name and version
                    package_match = re.match(r'(\w+)\s*=\s*["\']?([^"\']*)["\']?', line)
                    if package_match:
                        package_name = package_match.group(1)
                        version_spec = package_match.group(2).strip()
                        if version_spec and version_spec != '*':
                            requirements.append(f"{package_name}{version_spec}")
                        else:
                            requirements.append(package_name)
    
    return requirements

setup(
    name="bygod",
    version="2.0.1",
    author="Bible Gateway Downloader Team",
    author_email="ByGoD@rapdirabbit.software",
    description="A comprehensive, truly asynchronous tool for downloading Bible translations from BibleGateway.com",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/Christ-Is-The-King/bible-gateway-downloader",
    py_modules=["bible_downloader"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Religion",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_pipfile_requirements(),
    extras_require={
        "dev": read_pipfile_dev_requirements(),
    },
    entry_points={
        "console_scripts": [
            "bygod=bible_downloader:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "bible",
        "download",
        "biblegateway",
        "async",
        "scripture",
        "religion",
        "json",
        "csv",
        "xml",
        "yaml",
    ],
    project_urls={
        "Bug Reports": "https://github.com/Christ-Is-The-King/bible-gateway-downloader/issues",
        "Source": "https://github.com/Christ-Is-The-King/bible-gateway-downloader",
        "Documentation": "https://github.com/Christ-Is-The-King/bible-gateway-downloader#readme",
    },
)
