#!/usr/bin/env python3

"""Set up

This script is used to configure the package for distribution. It uses setuptools module to 
automatically discover all packages and subpackages. 

Attributes:
    - name: Name of the package.
    - version: Version of the package.
    - packages: All the Python packages in the project, found using find_packages(). 
"""

from setuptools import find_packages
from setuptools import setup


setup(
    name="XAgent",
    version="1.0.0",
    packages=find_packages()
)