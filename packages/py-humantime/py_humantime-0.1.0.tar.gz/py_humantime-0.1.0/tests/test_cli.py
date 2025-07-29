import unittest
import subprocess
import sys

SCRIPT = [sys.executable, '-m', 'pyhumantime.cli']

class TestCLI(unittest.TestCase):
    def run_cli(self, *args):
        result = subprocess.run(
            SCRIPT + list(args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf-8'
        )
        return result

    def test_to_human(self):
        result = self.run_cli('--to-human', '3661')
        self.assertEqual(result.stdout.strip(), '1h 1m 1s')
        self.assertEqual(result.returncode, 0)

    def test_to_seconds(self):
        result = self.run_cli('--to-seconds', '1h 1m 1s')
        self.assertEqual(result.stdout.strip(), '3661')
        self.assertEqual(result.returncode, 0)

    def test_invalid_input(self):
        result = self.run_cli('--to-seconds', 'notatime')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Error:', result.stderr)

    def test_mutually_exclusive(self):
        result = self.run_cli('--to-human', '10', '--to-seconds', '1m')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('error', result.stderr.lower())

if __name__ == '__main__':
    unittest.main() 