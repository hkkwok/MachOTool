from utils.header import Header, NonEncodingField, NullTerminatedStringField


class SectionBlock(Header):
    FIELDS = (
        NonEncodingField('seg_name'),
        NonEncodingField('sect_name'),
    )

    def __init__(self, seg_name, sect_name, bytes_):
        self.seg_name = None
        self.sect_name = None
        seg_name = NullTerminatedStringField.get_string(seg_name)
        sect_name = NullTerminatedStringField.get_string(sect_name)
        super(SectionBlock, self).__init__('Section: %s %s' % (seg_name, sect_name),
                                           seg_name=seg_name, sect_name=sect_name)
        self.parse_bytes(bytes_)

    def parse_bytes(self, bytes_):
        pass


class DataSection(SectionBlock):
    def __init__(self, sect_name, bytes_):
        sect_name = NullTerminatedStringField.get_string(sect_name)
        super(DataSection, self).__init__('__DATA', sect_name, bytes_)
        self.name = 'DataSection: %s' % sect_name


class TextSection(SectionBlock):
    def __init__(self, sect_name, bytes_):
        sect_name = NullTerminatedStringField.get_string(sect_name)
        super(TextSection, self).__init__('__TEXT', sect_name, bytes_)
        self.name = 'TextSection: %s' % sect_name


class NullTerminatedStringSection(TextSection):
    def __init__(self, sect_name, bytes_):
        self.name = None
        self._strings = dict()
        self._indices = list()
        super(NullTerminatedStringSection, self).__init__(sect_name, bytes_)

    def parse_bytes(self, bytes_):
        """
        Extract all NULL terminated strings from the given bytes. Record all their offsets.
        """
        s = ''
        offset = 0
        for idx in xrange(len(bytes_)):
            if bytes_[idx] == '\x00':
                self._strings[offset] = s
                self._indices.append(offset)
                s = ''
                offset = idx + 1
            else:
                s += bytes_[idx]

    def search(self, pattern):
        results = list()
        for (offset, string) in self._strings:
            if pattern in string:
                results.append(string)
        return results

    def num_strings(self):
        return len(self._strings)

    def item(self, index):
        offset = self._indices[index]
        return offset, self._strings[offset]

    def items(self):
        """
        Return a list of 2-tuple of (offset, string). Offsets are relative to the beginning of the section
        """
        # TODO - should create an iterator out of this function
        return sorted(self._strings.items(), lambda x, y: cmp(x[0], y[0]))

    def filter(self, pattern):
        indices = list()
        for (idx, offset) in enumerate(self._indices):
            if pattern in self._strings[offset]:
                indices.append(idx)
        return indices


class CstringSection(NullTerminatedStringSection):
    def __init__(self, bytes_):
        super(CstringSection, self).__init__('__cstring', bytes_)
        self.name = 'CstringSection: %d strings' % self.num_strings()


class ObjCMethodNameSection(NullTerminatedStringSection):
    def __init__(self, bytes_):
        super(ObjCMethodNameSection, self).__init__('__objc_methname', bytes_)
        self.name = 'ObjCMethodNameSection: %d strings' % self.num_strings()