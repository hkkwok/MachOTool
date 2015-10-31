from section_block import NullTerminatedStringSection


class StringMachOInfo(object):
    def __init__(self, desc, offset):
        self.desc = desc
        self.offset = offset
        self.string_sections = list()
        self.num_matched = 0
        self.num_strings = 0

    def add_section(self, seg_name, section, offset):
        assert isinstance(section, NullTerminatedStringSection)
        desc = '%s, %s' % (seg_name, section.sect_name)
        section_info = StringSectionInfo(desc, offset, section)
        self.string_sections.append(section_info)
        self.num_strings += section.num_strings()

    def filter(self, pattern):
        self.num_matched = sum([sect.filter(pattern) for sect in self.string_sections])
        return self.num_matched


class StringSectionInfo(object):
    def __init__(self, desc, offset, section):
        self.desc = desc
        self.offset = offset
        assert isinstance(section, NullTerminatedStringSection)
        self._section = section
        self._filter_mapping = None
        self.num_strings = self._section.num_strings()
        self.num_matched = 0

    def filter(self, pattern):
        self._filter_mapping = self._section.filter(pattern)
        self.num_matched = len(self._filter_mapping)
        return self.num_matched

    def string(self, matched_idx):
        assert 0 <= matched_idx < len(self._filter_mapping)
        return self._section.item(matched_idx)
