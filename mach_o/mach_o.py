from headers.mach_header import MachHeader, MachHeader64
from headers.load_command import LoadCommand
from headers.encryption_info_command import EncryptionInfoCommand, EncryptionInfoCommand64

from non_headers.encrypted_block import EncryptedBlock

from mach_o_parsers import LoadCommandParser, SectionParser, SegmentParser
from utils.header import HeaderInvalidValueError
from utils.progress_indicator import ProgressIndicator


class MachO(object):
    def __init__(self, mach_o_br):
        self.arch_width = None
        self.mach_header = None
        self.load_commands = list()
        self.segments = dict()
        self.linkedit_br = None
        self.encryption_info_commands = list()

        # Try to parse it as mach_header
        start = 0
        hdr_size = None
        try:
            hdr_size = MachHeader.get_size()
            self.mach_header = MachHeader(mach_o_br.bytes(start, hdr_size))
            self.arch_width = 32
        except HeaderInvalidValueError:
            pass

        # If fail, try mach_header_64
        if self.mach_header is None:
            try:
                hdr_size = MachHeader64.get_size()
                self.mach_header = MachHeader64(mach_o_br.bytes(start, hdr_size))
                self.arch_width = 64
            except ValueError:
                raise ValueError('mach_o: no valid mach header found')

        self.name = 'Mach-O: %s' % self.mach_header.FIELDS[1].display(self.mach_header)

        # Create a subrange for the parsed mach_header
        mach_header_br = mach_o_br.add_subrange(start, hdr_size)
        mach_header_br.data = self.mach_header

        # Parse each load commands
        lc_parser = LoadCommandParser(mach_o_br, self)
        start += hdr_size
        lc_size = LoadCommand.get_size()
        for idx in xrange(self.mach_header.ncmds):
            ProgressIndicator.display('parsing load command %d\n', idx)
            generic_lc = LoadCommand(mach_o_br.bytes(start, start + lc_size))
            lc_parser.parse(generic_lc, start)
            start += generic_lc.cmdsize

        # Add all data sections
        for (seg_name, segment_desc) in self.segments.items():
            for (sect_name, section_desc) in segment_desc.sections.items():
                ProgressIndicator.display('parsing section %s, %s\n', seg_name, sect_name)
                SectionParser(mach_o_br, self).parse(section_desc)

        # Add all encryption blocks
        for lc in self.encryption_info_commands:
            assert isinstance(lc, (EncryptionInfoCommand, EncryptionInfoCommand64))
            mach_o_br.insert_subrange(lc.cryptoff, lc.cryptsize, data=EncryptedBlock(lc.cryptid))

        # Add all segments
        for (seg_name, segment_desc) in self.segments.items():
            ProgressIndicator.display('parsing segment %s\n', seg_name)
            br = SegmentParser(mach_o_br).parse(segment_desc)
            if seg_name.startswith('__LINKEDIT'):
                self.linkedit_br = br

        ProgressIndicator.display('mach-o parsed\n')

    def is_section_encrypted(self, section):
        if len(self.encryption_info_commands) == 0:
            return False
        for enc_info in self.encryption_info_commands:
            if enc_info.is_encrypted() and enc_info.covers(section):
                return True
        return False
