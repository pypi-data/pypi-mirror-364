#!/usr/bin/env python3
"""Fast file finder and grep tool - combines find and grep functionality."""

import argparse
import fnmatch
import os
import re
import sys

from version import __version__

def find_files(directories, patterns):
    """Find files matching any of the given patterns in any of the directories."""
    for directory in directories:
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                for pattern in patterns:
                    if fnmatch.fnmatch(filename, pattern):
                        yield os.path.join(root, filename)
                        break  # Don't yield the same file multiple times

def grep_in_file(filepath, search_pattern, case_insensitive=False, line_numbers=False):
    """Search for pattern in a file and return matching lines."""
    matches = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            flags = re.IGNORECASE if case_insensitive else 0
            regex = re.compile(search_pattern, flags)

            for line_num, line in enumerate(f, 1):
                if regex.search(line):
                    line = line.rstrip('\n')
                    if line_numbers:
                        matches.append((line_num, line))
                    else:
                        matches.append(line)
    except (IOError, OSError) as e:
        print(f"Error reading {filepath}: {e}", file=sys.stderr)

    return matches


def _parse_targets(targets):
    """Separate directories from file patterns and apply defaults."""
    directories = []
    file_patterns = []

    for target in targets:
        if os.path.isdir(target):
            directories.append(target)
        else:
            # Handle extension shorthand like ".c" -> "*.c"
            if target.startswith('.') and not target.startswith('*.'):
                target = '*' + target
            file_patterns.append(target)

    # Set defaults
    if not directories:
        directories = ['.']
    if not file_patterns:
        file_patterns = ['*']

    return directories, file_patterns


def _print_matches(filepath, matches, filename_only, line_numbers):
    """Print matches according to the specified format options."""
    if filename_only:
        print(filepath)
    else:
        for match in matches:
            if line_numbers:
                line_num, line = match
                print(f"{filepath}:{line_num}:{line}")
            else:
                print(f"{filepath}:{match}")


def _search_files(directories, file_patterns, args):
    """Search files and print results."""
    found_matches = False

    for filepath in find_files(directories, file_patterns):
        matches = grep_in_file(filepath, args.regex, args.ignore_case, args.line_numbers)

        if matches:
            found_matches = True
            _print_matches(filepath, matches, args.filename_only, args.line_numbers)

    return 0 if found_matches else 1


def main():
    """Main function to parse arguments and execute file search and grep."""
    parser = argparse.ArgumentParser(
        description='Find files and grep for patterns - combines find and grep functionality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  ffgrep main "*.c"                 # Find main in all .c files
  ffgrep "def.*test" "*.py" -i      # Case-insensitive search for test functions
  ffgrep CONFIG_HIGHMEM .c          # Search .c files (auto-expands to *.c)
  ffgrep error "*.log" "*.txt" -l   # Search multiple file types with line numbers
  ffgrep main "*.c" src/ tests/     # Search in multiple directories
        '''
    )

    parser.add_argument('regex', help='Regular expression pattern to search for within files')
    parser.add_argument('targets', nargs='+',
                        help='File patterns (e.g., "*.c", ".py") '
                             'and/or directories to search')
    parser.add_argument('-i', '--ignore-case', action='store_true',
                        help='Case insensitive search')
    parser.add_argument('-l', '--line-numbers', action='store_true',
                        help='Show line numbers')
    parser.add_argument('-n', '--filename-only', action='store_true',
                        help='Show only filenames that contain matches')
    parser.add_argument('--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()
    directories, file_patterns = _parse_targets(args.targets)
    return _search_files(directories, file_patterns, args)

if __name__ == '__main__':
    sys.exit(main())
