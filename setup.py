#!/usr/bin/env python3
"""
Setup script for qwen-cli.
This file is kept for backward compatibility with older tools.

file: setup.py
"""

from setuptools import setup, find_packages
import os

# ✅ Read from root README.md (not docs/)
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="qwen-cli",
    description="A local, secure, AI-powered CLI assistant using Qwen via Ollama",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    license="MIT",
    url="https://github.com/MrFrey75/Qwen-CLI",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'requests'  # Add any runtime deps here later
    ],
    extras_require={
        "test": [
            "pytest>=7.0",
            "requests-mock>=1.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qwen=qwen_cli.__main__:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    include_package_data=True,
)