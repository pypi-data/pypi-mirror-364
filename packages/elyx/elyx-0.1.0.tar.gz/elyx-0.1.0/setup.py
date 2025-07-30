"""
Setup configuration for Elyx package
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="elyx",
    version="0.1.0",
    author="princecodes",
    author_email="princecodes@duck.com",
    description="A secure terminal-based encryption/decryption tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/elyx",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Security :: Cryptography",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=[
        "cryptography>=41.0.0",
        "rich>=13.7.0",
        "click>=8.1.0",
        "pyperclip>=1.8.2",
    ],
    entry_points={
        "console_scripts": [
            "elyx=elyx.main:main",
        ],
    },
    keywords="encryption decryption security cryptography terminal cli",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/elyx/issues",
        "Source": "https://github.com/yourusername/elyx",
    },
)