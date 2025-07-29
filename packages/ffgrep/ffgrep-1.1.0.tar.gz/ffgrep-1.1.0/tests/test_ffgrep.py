#!/usr/bin/env python3
"""Test suite for ffgrep functionality."""

import os
import shutil
import subprocess
import tempfile
import unittest

class TestFFGrep(unittest.TestCase):
    """Test cases for ffgrep command-line tool."""
    def setUp(self):
        """Set up test environment with temporary directory and test files."""
        self.test_dir = tempfile.mkdtemp()
        self.script_path = os.path.join(os.path.dirname(__file__), '..', 'ffgrep.py')

        # Create test files
        test_files = {
            'test.c': 'int main() {\n    printf("Hello");\n    return 0;\n}',
            'hello.py': 'def main():\n    print("hello world")\n',
            'config.txt': 'debug=true\nerror_log=/var/log/error.log\n',
            'subdir/app.js': 'function main() {\n    console.log("test");\n}',
        }

        for filepath, content in test_files.items():
            full_path = os.path.join(self.test_dir, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.test_dir)
    def run_ffgrep(self, *args):
        """Run ffgrep command with given arguments."""
        cmd = ['python3', self.script_path] + list(args)
        result = subprocess.run(cmd, cwd=self.test_dir, capture_output=True,
                                text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    def test_basic_search(self):
        """Test basic search functionality."""
        returncode, stdout, _ = self.run_ffgrep('main', '*.c')
        self.assertEqual(returncode, 0)
        self.assertIn('test.c', stdout)
        self.assertIn('main', stdout)

    def test_multiple_file_types(self):
        """Test searching in multiple file types."""
        returncode, stdout, _ = self.run_ffgrep('main', '*.py')
        self.assertEqual(returncode, 0)
        self.assertIn('hello.py', stdout)

    def test_case_insensitive(self):
        """Test case insensitive search."""
        returncode, stdout, _ = self.run_ffgrep('MAIN', '*.py', '-i')
        self.assertEqual(returncode, 0)
        self.assertIn('hello.py', stdout)

    def test_line_numbers(self):
        """Test line number display option."""
        returncode, stdout, _ = self.run_ffgrep('main', '*.c', '-l')
        self.assertEqual(returncode, 0)
        self.assertIn(':1:', stdout)  # Line number should appear

    def test_filename_only(self):
        """Test filename-only output option."""
        returncode, stdout, _ = self.run_ffgrep('main', '*.c', '-n')
        self.assertEqual(returncode, 0)
        lines = stdout.strip().split('\n')
        self.assertTrue(any('test.c' in line and ':' not in line for line in lines))

    def test_no_matches(self):
        """Test behavior when no matches are found."""
        returncode, stdout, _ = self.run_ffgrep('nonexistent', '*.c')
        self.assertEqual(returncode, 1)
        self.assertEqual(stdout.strip(), '')

    def test_no_files_match_pattern(self):
        """Test behavior when no files match the pattern."""
        returncode, _, _ = self.run_ffgrep('main', '*.nonexistent')
        self.assertEqual(returncode, 1)

    def test_subdirectory_search(self):
        """Test searching in subdirectories."""
        returncode, stdout, _ = self.run_ffgrep('main', '*.js')
        self.assertEqual(returncode, 0)
        self.assertIn('subdir/app.js', stdout)

    def test_regex_pattern(self):
        """Test regex pattern matching."""
        returncode, stdout, _ = self.run_ffgrep('def.*main', '*.py')
        self.assertEqual(returncode, 0)
        self.assertIn('hello.py', stdout)

    def test_extension_shorthand(self):
        """Test extension shorthand (.c -> *.c)."""
        returncode, stdout, _ = self.run_ffgrep('main', '.c')
        self.assertEqual(returncode, 0)
        self.assertIn('test.c', stdout)

    def test_multiple_patterns(self):
        """Test searching with multiple file patterns."""
        returncode, stdout, _ = self.run_ffgrep('main', '*.c', '*.py')
        self.assertEqual(returncode, 0)
        self.assertIn('test.c', stdout)
        self.assertIn('hello.py', stdout)

    def test_multiple_directories(self):
        """Test searching in multiple directories."""
        # Create another directory with files
        other_dir = os.path.join(self.test_dir, 'other')
        os.makedirs(other_dir)
        with open(os.path.join(other_dir, 'other.c'), 'w', encoding='utf-8') as f:
            f.write('int main() { return 1; }')

        returncode, stdout, _ = self.run_ffgrep('main', '*.c', '.', 'other')
        self.assertEqual(returncode, 0)
        self.assertIn('test.c', stdout)
        self.assertIn('other/other.c', stdout)

if __name__ == '__main__':
    unittest.main()
