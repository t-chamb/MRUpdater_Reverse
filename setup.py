#!/usr/bin/env python3
"""
Setup script for MRUpdater source code.
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mrupdater-source",
    version="1.0.0",
    author="MRUpdater Reverse Engineering Project",
    author_email="",
    description="Decompiled source code of ModRetro's MRUpdater application",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/mrupdater-source",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Hardware :: Universal Serial Bus (USB)",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "mrupdater=main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)