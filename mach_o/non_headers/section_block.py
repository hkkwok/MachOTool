from utils.header import Header, NonEncodingField, NullTerminatedStringField


class SectionBlock(Header):
    FIELDS = (
        NonEncodingField('seg_name'),
        NonEncodingField('sect_name'),
    )

    def __init__(self, seg_name, sect_name, bytes_):
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


class CstringSection(TextSection):
    def __init__(self, bytes_):
        self.name = 'CstringSection: 0 strings'
        self.strings = dict()
        super(CstringSection, self).__init__('__cstring', bytes_)

    def parse_bytes(self, bytes_):
        """
        Extract all NULL terminated strings from the given bytes. Record all their offsets.
        """
        s = ''
        offset = 0
        for idx in xrange(len(bytes_)):
            if bytes_[idx] == '\x00':
                self.strings[s] = offset
                s = ''
                offset = idx + 1
            else:
                s += bytes_[idx]

    def search(self, pattern):
        results = list()
        for (string, offset) in self.strings:
            if pattern in string:
                results.append(string)
        return results

    def items(self):
        """
        Return a list of 2-tuple of (string, offset). Offsets are relative to the beginning of the section
        """
        return sorted(self.strings.items(), lambda x, y: cmp(x[1], y[1]))
