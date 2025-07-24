#!/usr/bin/env python3
"""Setup script for Hippodrome Solver utilities."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="hippodrome-solver",
    version="1.0.0",
    author="Hippodrome Solver Team",
    description="A high-performance puzzle solver for the Hippodrome chess puzzle",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/hippodrome-solver",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment :: Puzzle Games",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "flask>=2.0.0",
        "flask-cors>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
        ],
        "web": [
            "gunicorn>=20.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "hippodrome-visualize=visualize_solution:main",
            "hippodrome-validate=validate_solutions:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/yourusername/hippodrome-solver/issues",
        "Source": "https://github.com/yourusername/hippodrome-solver",
        "Documentation": "https://github.com/yourusername/hippodrome-solver/wiki",
    },
) 