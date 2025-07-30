#!/usr/bin/env python3
"""
Setup script for IronShield Python package.
"""

from setuptools import setup, find_packages
import os

# Read the README file
current_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_dir, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ironshield",
    version="0.0.1",
    author="IronShield Tech",
    author_email="tech@ironshield.dev",
    description="IronShield - A comprehensive security toolkit for Python applications",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IronShield-Tech/ironshield-js",
    project_urls={
        "Bug Reports": "https://github.com/IronShield-Tech/ironshield-js/issues",
        "Source": "https://github.com/IronShield-Tech/ironshield-js",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="security ironshield protection python security-toolkit",
    python_requires=">=3.7",
    install_requires=[
        # No dependencies for placeholder package
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "ironshield=ironshield.cli:main",
        ],
    },
) 