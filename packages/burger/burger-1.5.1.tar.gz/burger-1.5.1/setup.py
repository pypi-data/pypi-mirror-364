#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Generated with burger.create_setup_py()
"""

import io
import os
import setuptools

# Ensure the working directory is captured
CWD = os.path.dirname(os.path.abspath(__file__))

# Read the file into LONG_DESCRIPTION using utf-8
with io.open(os.path.join(CWD, "README.rst"), encoding="utf-8") as fp:
    LONG_DESCRIPTION = fp.read()

# Data lovingly ripped off from a toml file
SETUP_ARGS = {
    "name": "burger",
    "version": "1.5.1",
    "description": "Burger Becky's shared python library.",
    "license": "MIT",
    "python_requires": ">=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*",
    "install_requires": [
        "setuptools >= 44.0.0",
        "wslwinreg >= 1.1.2",
    ],
    "classifiers": [
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    "keywords": [
        "burger",
        "perforce",
        "burgerlib",
        "development",
        "python",
        "windows",
    ],
    "platforms": [
        "Any",
    ],
    "url": "https://github.com/burgerbecky/pyburger",
    "license_file": "LICENSE.txt",
    "long_description": LONG_DESCRIPTION,
    "packages": [
        "burger",
    ],
}

# Pass metadata to pip for old python versions

if __name__ == "__main__":
    setuptools.setup(**SETUP_ARGS)
