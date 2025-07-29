#!/usr/bin/env python3

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()

# Read requirements if they exist
def read_requirements():
    try:
        with open('requirements.txt') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

setup(
    name='ffgrep',
    version='1.0.0',
    description='Fast file finder and grep tool - combines find and grep functionality',
    long_description=read_readme(),
    long_description_content_type='text/markdown',
    author='Rob Adams',
    author_email='',
    url='https://github.com/pastor-robert/ffgrep',
    license='MIT',
    
    # Package configuration
    py_modules=['ffgrep'],
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
        'License :: OSI Approved :: MIT License',
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