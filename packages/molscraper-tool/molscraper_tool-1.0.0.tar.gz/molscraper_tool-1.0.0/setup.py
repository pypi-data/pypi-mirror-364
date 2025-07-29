#!/usr/bin/env python3
"""
Setup script for Molecule Scraper - pip distribution
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "A comprehensive tool for extracting chemical compound data from PubChem"

# Read requirements
def read_requirements():
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            return [line.strip() for line in fh if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return ["pandas>=1.5.0", "requests>=2.28.0", "openpyxl>=3.0.0"]

setup(
    name="molscraper-tool",
    version="1.0.0",
    author="Xhuliano Brace, Timothy Chia",
    author_email="x@rhizome-research.com, tim@rhizome-research.com",
    description="Chemical data extraction tool for researchers and chemists",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    
    # Package configuration
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    
    # Include additional files
    include_package_data=True,
    package_data={
        "molscraper": [
            "pyarmor_runtime_*/__init__.py",
            "pyarmor_runtime_*/*.so",
            "pyarmor_runtime_*/*.dll",
            "pyarmor_runtime_*/*.dylib"
        ],
    },
    
    # Dependencies
    install_requires=read_requirements(),
    
    # CLI entry points
    entry_points={
        "console_scripts": [
            "molscraper=molscraper.cli:main",
        ],
    },
    
    # Metadata
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research", 
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Chemistry",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    
    # Requirements
    python_requires=">=3.8",
    
    # Keywords for searchability
    keywords=[
        "chemistry", "pubchem", "chemical-data", "molecules",
        "research", "cas-numbers", "chemical-properties",
        "data-extraction", "scientific-computing", "cheminformatics"
    ],
    
    # Project URLs
    project_urls={
        "Documentation": "https://github.com/xhuliano/molscraper#readme",
        "Bug Reports": "https://github.com/xhuliano/molscraper/issues",
        "Source": "https://github.com/xhuliano/molscraper",
    },
) 