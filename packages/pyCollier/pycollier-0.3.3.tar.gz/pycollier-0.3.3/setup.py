#!/usr/bin/env python3

from pathlib import Path
import re

import setuptools
import skbuild


project_dir = Path(__file__).parent

# Import the README and use it as the long-description.
with open(project_dir.joinpath('README.md')) as f:
    LONG_DESCRIPTION = '\n' + f.read()

# Load the package's __version__.py module as a dictionary.
info = {}
with open(project_dir.joinpath('pyCollier', '__info__.py')) as f:
    exec(f.read(), info)


# Package meta-data.
NAME = 'pyCollier'
DESCRIPTION = 'access COLLIER loop functions via python'
URL = ''
EMAIL = ''
REQUIRES_PYTHON = '>=3.6, <4'
AUTHORS = info['__authors__']
VERSION = info['__version__']
REQUIRED = [
    "numpy>=1.13.0,<2"
]

EXTRAS_DOCS = [
]

EXTRAS_TEST = [
]

EXTRAS_EXAMPLES = [
]

with open("CMakeLists.txt", "r") as cmakelists:
    content = cmakelists.read()
    try:
        cmakeVersion = re.findall(
            r"cmake_minimum_required\(\W*VERSION\W*([0-9\.]+)\W*\)",
            content,
            re.MULTILINE | re.IGNORECASE,
        )[0]
    except IndexError:
        raise skbuild.exceptions.SKBuildError(
            "Could not read cmake and project version from CMakeLists.txt"
        )

skbuild.setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHORS,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=setuptools.find_packages(),
    install_requires=REQUIRED,
    extras_require={
        "docs": EXTRAS_DOCS,
        "test": EXTRAS_TEST,
        "examples": EXTRAS_EXAMPLES,
    },
    include_package_data=True,
    license='MIT',
    classifiers=[
        # Trove classifiers
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    # $ setup.py publish support.
    cmdclass={
    },
)
