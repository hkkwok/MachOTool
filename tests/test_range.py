import unittest
from utils.range import Range


class TestRange(unittest.TestCase):
    def test_operators(self):
        a = Range(0, 5)
        self.assertEqual(5, len(a))  # verify that len() is correct
        self.assertEqual('<Range:0-5>', str(a))

        self.assertTrue(a == a)
        self.assertTrue(a <= a)
        self.assertTrue(a >= a)
        self.assertFalse(a < a)
        self.assertFalse(a > a)
        self.assertFalse(a != a)

        # Overlaps 'b'.
        b = Range(1, 6)
        self.assertTrue(a <= b)
        self.assertFalse(a < b)
        self.assertFalse(a >= b)
        self.assertFalse(a > b)
        self.assertFalse(a == b)
        self.assertTrue(a != b)

        # Does not overlap 'c'.
        c = Range(5, 7)
        self.assertTrue(a < c)
        self.assertFalse(a <= c)
        self.assertFalse(a > c)
        self.assertFalse(a >= c)
        self.assertFalse(a == c)
        self.assertTrue(a != c)
        self.assertFalse(a in c)
        self.assertFalse(c in a)

        # A strict superset of 'd'.
        d = Range(2, 4)
        self.assertTrue(a <= d)
        self.assertFalse(a < d)
        self.assertFalse(a >= d)
        self.assertFalse(a > d)
        self.assertFalse(a == d)
        self.assertTrue(a != d)
        self.assertTrue(d in a)
        self.assertFalse(a in d)

    def test_errors(self):
        self.assertRaises(ValueError, lambda: Range(-1, 2))
        self.assertRaises(ValueError, lambda: Range(0, -1))
        self.assertRaises(ValueError, lambda: Range(2, 1))
