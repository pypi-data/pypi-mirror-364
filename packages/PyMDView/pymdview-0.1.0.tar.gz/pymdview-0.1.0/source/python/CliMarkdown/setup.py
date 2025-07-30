#!/usr/bin/env python3
"""
Setup script for CLI Markdown Viewer
"""

from setuptools import setup, find_packages

setup(
    name="cli-markdown",
    version="0.1.0",
    description="A command line tool to display Markdown files",
    author="CLI Markdown Team",
    packages=find_packages(),
    install_requires=[
        "rich>=10.0.0",
        "markdown-it-py>=2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "mdview=source.python.CliMarkdown.cli_markdown:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
)
