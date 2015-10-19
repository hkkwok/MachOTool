import unittest
from utils.byte_range import ByteRange


class TestBytesRange(unittest.TestCase):
    def check_subrange(self, subrange, expected_start, expected_stop):
        self.assertEqual(expected_start, subrange.start)
        self.assertEqual(expected_stop, subrange.stop)

    def check_subranges(self, byte_range, *expected):
        expected_len = len(expected)
        self.assertEqual(expected_len, len(byte_range.subranges))
        for idx in xrange(expected_len):
            self.check_subrange(byte_range.subranges[idx], *expected[idx])

    def check_partition(self, byte_range, expected):
        assert isinstance(byte_range, ByteRange)
        assert isinstance(expected, bool)
        self.assertEqual(expected, byte_range.does_partition())

    def check_partitions(self, *params):
        assert len(params) % 2 == 0
        for idx in xrange(0, len(params), 2):
            self.check_partition(params[idx], params[idx+1])

    def test_add_subrange(self):
        """
        Test add_subrange() method
        """
        br = ByteRange(0, 1000)

        self.check_partition(br, True)
        self.assertEqual('<BytesRange:0-1000>', str(br))

        # Add 1st subrange
        br.add_subrange(offset=100, length=51)
        self.check_partition(br, False)
        self.check_subranges(br, (100, 151))

        # Add a subrange in the front
        br.add_subrange(offset=50, length=7)
        self.check_partition(br, False)
        self.check_subranges(br, (50, 57), (100, 151))

        # Add a subrange in the end
        br.add_subrange(offset=200, length=800)
        self.check_partition(br, False)
        self.check_subranges(br, (50, 57), (100, 151), (200, 1000))

        # Fill out the remaining gap to completely cover the byte range
        br.add_subrange(offset=0, length=50)
        br.add_subrange(offset=57, length=43)
        br.add_subrange(offset=151, length=49)
        self.check_partition(br, True)
        self.check_subranges(br, (0, 50), (50, 57), (57, 100), (100, 151), (151, 200), (200, 1000))

    def test_nested_subranges(self):
        """
        Test nested subranges methods
        """
        br1 = ByteRange(0, 100)
        self.check_partitions(br1, True)

        # Add 2nd layer
        br11 = br1.add_subrange(0, 20)
        self.check_partitions(br1, False, br11, True)

        br12 = br1.add_subrange(20, 50)
        self.check_partitions(br1, False, br12, True)

        br13 = br1.add_subrange(70, 30)
        self.check_partitions(br1, True, br13, True)

        # Add 3rd layer
        br121 = br12.add_subrange(0, 30)
        self.check_partitions(br1, False, br12, False, br121, True)

        br122 = br12.add_subrange(30, 20)
        self.check_partitions(br1, True, br12, True, br122, True)

        # Add 4th layer
        br1211 = br121.add_subrange(0, 15)
        self.check_partitions(br1, False, br12, False, br121, False, br1211, True)

        br1212 = br121.add_subrange(15, 10)
        self.check_partitions(br1, False, br12, False, br121, False, br1212, True)

        br1213 = br121.add_subrange(25, 5)
        self.check_partitions(br1, True, br12, True, br121, True, br1213, True)

        # Verify all the absolute offsets
        self.assertEqual((0, 20), br11.abs_range())
        self.assertEqual((20, 35), br1211.abs_range())
        self.assertEqual((35, 45), br1212.abs_range())
        self.assertEqual((45, 50), br1213.abs_range())
        self.assertEqual((50, 70), br122.abs_range())
        self.assertEqual((70, 100), br13.abs_range())

    def test_errors(self):
        br = ByteRange(0, 100)

        # Add 2 subranges
        br.add_subrange(20, 10)
        br.add_subrange(60, 20)

        # Add an overlapping subrange in front of 1st subrange
        self.assertRaises(ValueError, lambda: br.add_subrange(0, 21))

        # Add an overlapping subrange behind 1st subrange
        self.assertRaises(ValueError, lambda: br.add_subrange(29, 20))

        # Add an overlapping subrange in front of 2nd subrange
        self.assertRaises(ValueError, lambda: br.add_subrange(35, 26))

        # Add an overlapping subrange behind 2nd subrange
        self.assertRaises(ValueError, lambda: br.add_subrange(79, 10))

        # Add a subrange that goes beyond the parent byte range
        self.assertRaises(ValueError, lambda: br.add_subrange(90, 11))
