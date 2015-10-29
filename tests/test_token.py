from ui.cli.token import *
import unittest


class TestToken(unittest.TestCase):
    def test_keyword_token(self):
        keyword = 'show-all'
        token = KeywordToken(keyword)
        for idx in xrange(1, len(keyword)):
            self.assertTrue(token.accept(keyword[:idx]))
        self.assertFalse(token.accept('li'))

        for idx in xrange(1, len(keyword)-1):
            self.assertFalse(token.is_complete(keyword[:idx]))
        self.assertTrue(token.is_complete(keyword))

        self.assertTrue(token.is_keyword())
        self.assertFalse(token.is_parameter())

    def test_string_token(self):
        token = StringToken('value')

        self.assertTrue(token.accept('abc xyz'))

        self.assertTrue(token.is_complete('abc xyz'))
        self.assertFalse(token.is_complete(''))

        self.assertFalse(token.is_keyword())
        self.assertTrue(token.is_parameter())

    def test_int_token(self):
        token = IntegerToken('value')

        self.assertTrue(token.accept('123'))
        self.assertFalse(token.accept('12abc'))

        self.assertTrue(token.is_complete('123'))
        self.assertFalse(token.is_complete(''))

        self.assertFalse(token.is_keyword())
        self.assertTrue(token.is_parameter())

    def test_hex_token(self):
        token = HexToken('value')

        self.assertTrue(token.accept('0'))
        self.assertTrue(token.accept('0x'))
        self.assertTrue(token.accept('0x123'))

        self.assertFalse(token.is_complete('0'))
        self.assertFalse(token.is_complete('0x'))
        self.assertTrue(token.is_complete('0x1'))

        self.assertFalse(token.is_keyword())
        self.assertTrue(token.is_parameter())
