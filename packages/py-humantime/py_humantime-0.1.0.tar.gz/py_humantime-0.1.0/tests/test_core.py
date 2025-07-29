import unittest
from pyhumantime.core import HumanTimeConverter

class TestHumanTimeConverter(unittest.TestCase):
    def test_seconds_to_human_basic(self):
        self.assertEqual(HumanTimeConverter.seconds_to_human(0), '0s')
        self.assertEqual(HumanTimeConverter.seconds_to_human(59), '59s')
        self.assertEqual(HumanTimeConverter.seconds_to_human(60), '1m')
        self.assertEqual(HumanTimeConverter.seconds_to_human(61), '1m 1s')
        self.assertEqual(HumanTimeConverter.seconds_to_human(3600), '1h')
        self.assertEqual(HumanTimeConverter.seconds_to_human(3661), '1h 1m 1s')

    def test_seconds_to_human_invalid(self):
        with self.assertRaises(ValueError):
            HumanTimeConverter.seconds_to_human(-1)
        with self.assertRaises(ValueError):
            HumanTimeConverter.seconds_to_human('abc')

    def test_human_to_seconds_basic(self):
        self.assertEqual(HumanTimeConverter.human_to_seconds('0s'), 0)
        self.assertEqual(HumanTimeConverter.human_to_seconds('59s'), 59)
        self.assertEqual(HumanTimeConverter.human_to_seconds('1m'), 60)
        self.assertEqual(HumanTimeConverter.human_to_seconds('1m 1s'), 61)
        self.assertEqual(HumanTimeConverter.human_to_seconds('1h'), 3600)
        self.assertEqual(HumanTimeConverter.human_to_seconds('1h 1m 1s'), 3661)
        self.assertEqual(HumanTimeConverter.human_to_seconds('1h 15m'), 4500)

    def test_human_to_seconds_invalid(self):
        with self.assertRaises(ValueError):
            HumanTimeConverter.human_to_seconds('')
        with self.assertRaises(ValueError):
            HumanTimeConverter.human_to_seconds('abc')
        with self.assertRaises(ValueError):
            HumanTimeConverter.human_to_seconds(123)

if __name__ == '__main__':
    unittest.main() 