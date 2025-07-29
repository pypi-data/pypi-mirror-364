import unittest
from app_math.checker import is_even, is_odd

class TestAppMath(unittest.TestCase):
    def test_even(self):
        self.assertTrue(is_even(2))
        self.assertTrue(is_even(0))
        self.assertFalse(is_even(3))

    def test_odd(self):
        self.assertTrue(is_odd(1))
        self.assertFalse(is_odd(4))

if __name__ == "__main__":
    unittest.main()
