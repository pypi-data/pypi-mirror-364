# ffgrep

[![CI](https://github.com/pastor-robert/ffgrep/actions/workflows/ci.yml/badge.svg)](https://github.com/pastor-robert/ffgrep/actions/workflows/ci.yml)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A fast file finder and grep tool that combines the functionality of `find` and `grep` into a single command.

*Developed with assistance from Claude AI by Anthropic.*

## Overview

`ffgrep` replaces the common pattern of `find . -name '*.ext' | xargs grep pattern` with a simpler, more efficient command. It recursively searches for files matching a pattern and greps for content within those files.

## Installation

Simply clone this repository and make the script executable:

```bash
git clone https://github.com/your-username/ffgrep.git
cd ffgrep
chmod +x ffgrep.py
```

Optionally, create a symlink to use it system-wide:

```bash
ln -s $(pwd)/ffgrep.py /usr/local/bin/ffgrep
```

## Usage

```bash
./ffgrep.py [options] <regex> <targets...>
```

### Arguments

- `regex`: Regular expression pattern to search for within files
- `targets`: File patterns (e.g., "*.c", ".py") and/or directories to search

### Options

- `-i, --ignore-case`: Case insensitive search
- `-l, --line-numbers`: Show line numbers
- `-n, --filename-only`: Show only filenames that contain matches

### Examples

```bash
# Find 'main' function in all C files
./ffgrep.py main "*.c"

# Extension shorthand - .c expands to *.c
./ffgrep.py CONFIG_HIGHMEM .c

# Case-insensitive search for test functions in Python files
./ffgrep.py "def.*test" "*.py" -i

# Show line numbers for error messages in log files
./ffgrep.py error "*.log" -l

# Search multiple file types
./ffgrep.py error "*.log" "*.txt" -l

# Search in multiple directories
./ffgrep.py main "*.c" src/ tests/

# Just show filenames containing TODO comments
./ffgrep.py TODO "*.py" -n
```

## Features

- **Fast**: Uses generators to avoid loading all file paths into memory
- **Flexible**: Supports multiple file patterns and directories in a single command
- **Smart**: Extension shorthand (`.c` expands to `*.c`)
- **Powerful**: Full regex support for content search
- **Portable**: Single Python script with no external dependencies
- **Unix-friendly**: Follows Unix conventions for exit codes and output format

## Requirements

- Python 3.6+
- No external dependencies

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Exit Codes

- `0`: Matches found
- `1`: No matches found or error occurred