class ByteRangeParser(object):
    def __init__(self, byte_range):
        self.byte_range = byte_range
        self.start = None
        self.cmd_size = None
        self.current = None

    def initialize(self, start, cmd_size):
        self.start = start
        self.cmd_size = cmd_size
        self.current = self.start

    def add_subrange(self, data=None, length=None):
        if length is None:
            length = self.start + self.cmd_size - self.current
        br = self.byte_range.add_subrange(self.current, length, data=data)
        self.current += length
        return br

    def add_subrange_beneath(self, data=None, length=None):
        if length is None:
            length = self.cmd_size
        return self.byte_range.insert_subrange(self.start, length, data=data)

    def _get_bytes(self, length=None):
        if length is None:
            length = self.start + self.cmd_size - self.current
        return self.byte_range.bytes(self.current, self.current + length)

    def _add_padding(self, desc, offset=None):
        if offset is None:
            offset = self.cmd_size
        gap = self.start + offset - self.current
        if gap != 0:
            assert gap > 0  # there is a gap in front
            self.add_subrange(desc, gap)
