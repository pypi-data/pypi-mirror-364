"""
Setup script for IPC Framework
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ipc-framework",
    version="1.0.0",
    author="IPC Framework Team",
    author_email="ifesol@example.com",
    description="Efficient Inter-Process Communication Framework with hierarchical application and channel management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ifesol/ipc-framework",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies for core functionality
    ],
    extras_require={
        "examples": ["psutil>=5.8.0"],
        "dev": ["pytest>=6.0.0", "black>=21.0.0"],
    },
    entry_points={
        "console_scripts": [
            "ipc-server=examples.basic_server:main",
        ],
    },
) 