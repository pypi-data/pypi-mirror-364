#!/usr/bin/env python3

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

class TestFFGrep(unittest.TestCase):
    
    def setUp(self):
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
            with open(full_path, 'w') as f:
                f.write(content)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir)
    
    def run_ffgrep(self, *args):
        cmd = ['python3', self.script_path] + list(args)
        result = subprocess.run(cmd, cwd=self.test_dir, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    
    def test_basic_search(self):
        returncode, stdout, stderr = self.run_ffgrep('main', '*.c')
        self.assertEqual(returncode, 0)
        self.assertIn('test.c', stdout)
        self.assertIn('main', stdout)
    
    def test_multiple_file_types(self):
        returncode, stdout, stderr = self.run_ffgrep('main', '*.py')
        self.assertEqual(returncode, 0)
        self.assertIn('hello.py', stdout)
    
    def test_case_insensitive(self):
        returncode, stdout, stderr = self.run_ffgrep('MAIN', '*.py', '-i')
        self.assertEqual(returncode, 0)
        self.assertIn('hello.py', stdout)
    
    def test_line_numbers(self):
        returncode, stdout, stderr = self.run_ffgrep('main', '*.c', '-l')
        self.assertEqual(returncode, 0)
        self.assertIn(':1:', stdout)  # Line number should appear
    
    def test_filename_only(self):
        returncode, stdout, stderr = self.run_ffgrep('main', '*.c', '-n')
        self.assertEqual(returncode, 0)
        lines = stdout.strip().split('\n')
        self.assertTrue(any('test.c' in line and ':' not in line for line in lines))
    
    def test_no_matches(self):
        returncode, stdout, stderr = self.run_ffgrep('nonexistent', '*.c')
        self.assertEqual(returncode, 1)
        self.assertEqual(stdout.strip(), '')
    
    def test_no_files_match_pattern(self):
        returncode, stdout, stderr = self.run_ffgrep('main', '*.nonexistent')
        self.assertEqual(returncode, 1)
    
    def test_subdirectory_search(self):
        returncode, stdout, stderr = self.run_ffgrep('main', '*.js')
        self.assertEqual(returncode, 0)
        self.assertIn('subdir/app.js', stdout)
    
    def test_regex_pattern(self):
        returncode, stdout, stderr = self.run_ffgrep('def.*main', '*.py')
        self.assertEqual(returncode, 0)
        self.assertIn('hello.py', stdout)
    
    def test_extension_shorthand(self):
        returncode, stdout, stderr = self.run_ffgrep('main', '.c')
        self.assertEqual(returncode, 0)
        self.assertIn('test.c', stdout)
    
    def test_multiple_patterns(self):
        returncode, stdout, stderr = self.run_ffgrep('main', '*.c', '*.py')
        self.assertEqual(returncode, 0)
        self.assertIn('test.c', stdout)
        self.assertIn('hello.py', stdout)
    
    def test_multiple_directories(self):
        # Create another directory with files
        other_dir = os.path.join(self.test_dir, 'other')
        os.makedirs(other_dir)
        with open(os.path.join(other_dir, 'other.c'), 'w') as f:
            f.write('int main() { return 1; }')
        
        returncode, stdout, stderr = self.run_ffgrep('main', '*.c', '.', 'other')
        self.assertEqual(returncode, 0)
        self.assertIn('test.c', stdout)
        self.assertIn('other/other.c', stdout)

if __name__ == '__main__':
    unittest.main()