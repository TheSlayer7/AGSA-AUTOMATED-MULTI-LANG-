"""
Setup file for the DigiLocker mock package.
"""

from setuptools import setup, find_packages

setup(
    name="digilocker-mock",
    version="1.0.0",
    description="Mock implementation of DigiLocker API for development and testing",
    author="AGSA Development Team",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        # No external dependencies for the mock package
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
