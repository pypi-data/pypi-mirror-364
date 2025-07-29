#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="enhanced-chinese-translator",
    version="1.0.1",
    author="Enhanced Chinese Translator Team",
    author_email="support@enhanced-translator.com",
    description="High-performance Chinese to English translation tool with multi-threading and batch processing",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/jasonlau233/enhanced_chinese_translator",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Internationalization",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "enhanced-chinese-translator=enhanced_chinese_translator.translator:main",
            "ect=enhanced_chinese_translator.translator:main",
        ],
    },
    keywords="chinese translation english batch multi-threading concurrent api google baidu",
    project_urls={
        "Bug Reports": "https://github.com/jasonlau233/enhanced_chinese_translator/issues",
        "Source": "https://github.com/jasonlau233/enhanced_chinese_translator",
        "Documentation": "https://github.com/jasonlau233/enhanced_chinese_translator/wiki",
    },
    include_package_data=True,
    zip_safe=False,
)