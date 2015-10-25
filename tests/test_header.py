import unittest
import time
from utils.header import *


class TestFields(unittest.TestCase):
    def setUp(self):
        self.value = None

    def test_field(self):
        field = Field('value', 'I')
        self.value = 12345678
        self.assertTrue(field.validate(self))
        self.assertEqual('12345678', field.display(self))

    def test_hex_field(self):
        hex_field = HexField('value', 'I')
        self.value = 0xdeadbeef
        self.assertTrue(hex_field.validate(self))
        self.assertEqual('0xdeadbeef', hex_field.display(self))

    def test_magic_field(self):
        magic_field = MagicField('value', 'I', {0x1111: 'ONES', 0x2222: 'TWOS'})
        self.value = 0x1111
        self.assertTrue(magic_field.validate(self))
        self.assertEqual('ONES', magic_field.display(self))

        self.value = 0x2222
        self.assertTrue(magic_field.validate(self))
        self.assertEqual('TWOS', magic_field.display(self))

        self.value = 0x3333
        self.assertFalse(magic_field.validate(self))
        self.assertEqual('0x3333', magic_field.display(self))

    def test_unix_time_field(self):
        unix_time_field = UnixTimeField('value', 'I')
        current = int(time.time())
        self.value = current
        self.assertTrue(unix_time_field.validate(self))
        self.assertEqual(time.strftime(unix_time_field.FORMAT, time.localtime(current)),
                         unix_time_field.display(self))

    def test_version_field(self):
        version_field = VersionField('value', 'I')
        self.value = 0x00010305
        self.assertTrue(version_field.validate(self))
        self.assertEqual('1.3.5', version_field.display(self))

        self.value = 0x80008080
        self.assertEqual('32768.128.128', version_field.display(self))

    def test_bitfields(self):
        bitfields = BitFields('value', 'C', {'BIT0': 0x1, 'BIT1': 0x2, 'BIT2': 0x4, 'BIT3': 0x8})
        self.value = 0x09
        self.assertTrue(bitfields.validate(self))
        self.assertEqual('BIT3,BIT0', bitfields.display(self))

        self.value = 0x06
        self.assertTrue(bitfields.validate(self))
        self.assertEqual('BIT2,BIT1', bitfields.display(self))

        self.value = 0x10
        self.assertFalse(bitfields.validate(self))

    def test_enum_field(self):
        enum_field = EnumField('value', 'I',
                               {'A': 1,
                                'B': 2,
                                'C': 3})
        self.value = 1
        self.assertTrue(enum_field.validate(self))
        self.assertEqual('A', enum_field.display(self))

        self.value = 2
        self.assertTrue(enum_field.validate(self))
        self.assertEqual('B', enum_field.display(self))

        self.value = 3
        self.assertTrue(enum_field.validate(self))
        self.assertEqual('C', enum_field.display(self))

        self.value = 4
        self.assertFalse(enum_field.validate(self))

    def test_null_terminated_string_field(self):
        string_field = NullTerminatedStringField('value', 'I')
        self.value = 'abcdef\0\0'
        self.assertTrue(string_field.validate(self))
        self.assertEqual('abcdef', string_field.display(self))
