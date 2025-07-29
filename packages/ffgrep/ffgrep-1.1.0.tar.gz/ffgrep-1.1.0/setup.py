#!/usr/bin/env python3
"""Setup script for ffgrep package."""

import os
from setuptools import setup

from version import __version__

# Read the README file
def read_readme():
    """Read the README file for long description."""
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

# Read requirements if they exist
def read_requirements():
    """Read requirements from requirements.txt file."""
    try:
        with open('requirements.txt', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

setup(
    name='ffgrep',
    version=__version__,
    description='Fast file finder and grep tool - combines find and grep functionality',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Rob Adams',
    author_email='',
    url='https://github.com/pastor-robert/ffgrep',
    license='MIT',

    # Package configuration
    py_modules=['ffgrep', 'version'],
    python_requires='>=3.6',
    install_requires=read_requirements(),

    # Console script entry point
    entry_points={
        'console_scripts': [
            'ffgrep=ffgrep:main',
        ],
    },

    # Package metadata
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: General',
        'Topic :: Utilities',
    ],

    keywords='grep find search files regex pattern matching',
    zip_safe=False,
)
