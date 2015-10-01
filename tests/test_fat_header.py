import unittest
from mach_o.headers.fat_header import FatHeader
from utils.header import HeaderInvalidValueError, HeaderSizeError


class TestFatHeader(unittest.TestCase):
    def test_decode(self):
        hdr = FatHeader('\xca\xfe\xba\xbe\x00\x00\x00\x03')
        self.assertEqual(3, hdr.nfat_arch)
        self.assertEqual(FatHeader.MAGIC, hdr.magic)

        self.assertEqual('<fat_header: magic=MAGIC, nfat_arch=3>', str(hdr))

        # bad magic
        self.assertRaises(HeaderInvalidValueError, lambda: FatHeader('\xca\xfe\xba\xff\x01\x02\x03\x04'))

        # given 9 bytes for a 8-bytes header
        self.assertRaises(HeaderSizeError, lambda: FatHeader('\xca\xfe\xba\xfe\x01\x02\x03\x04\x00'))