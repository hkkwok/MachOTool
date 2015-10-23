import unittest
from utils.commafy import commafy


class TestCommafy(unittest.TestCase):
    def test_commafy(self):
        self.assertEqual('123', commafy(123))
        self.assertEqual('12,345', commafy(12345))
        self.assertEqual('1,234,567', commafy(1234567))
        self.assertEqual('1,234.5678', commafy(1234.5678))
