from headers.mach_header import MachHeader, MachHeader64
from headers.load_command import LoadCommand
from headers.segment_command import SegmentCommand, SegmentCommand64
from headers.symtab_command import SymtabCommand
from headers.dysymtab_command import DysymtabCommand
from headers.dylib_command import DylibCommand
from headers.version_min_command import VersionMinCommand
from headers.source_version_command import SourceVersionCommand
from headers.entry_point_command import EntryPointCommand
from headers.linkedit_data_command import LinkeditDataCommand
from headers.uuid_command import UuidCommand
from headers.dylinker_command import DylinkerCommand
from headers.dyld_info_command import DyldInfoCommand
from headers.sub_framework_command import SubFrameworkCommand
from headers.sub_client_command import SubClientCommand
from headers.sub_umbrella_command import SubUmbrellaCommand
from headers.sub_library_command import SubLibraryCommand
from headers.prebound_dylib_command import PreboundDylibCommand
from headers.twolevel_hints_command import TwolevelHintsCommand
from headers.prebind_cksum_command import PrebindCksumCommand
from headers.encryption_info_command import EncryptionInfoCommand, EncryptionInfoCommand64
from headers.linker_option_command import LinkerOptionCommand

from mach_o_parsers import LoadCommandParser, SectionParser, SegmentParser
from utils.header import HeaderInvalidValueError
from utils.progress_indicator import ProgressIndicator


class MachO(object):
    # Load commands for 32-bit architectures
    COMMANDS_32 = {
        'LC_SEGMENT': SegmentCommand,
        'LC_SYMTAB': SymtabCommand,
        'LC_DYSYMTAB': DysymtabCommand,
        'LC_LOAD_DYLIB': DylibCommand,
        'LC_LOAD_WEAK_DYLIB': DylibCommand,
        'LC_ID_DYLIB': DylibCommand,
        'LC_VERSION_MIN_MACOSX': VersionMinCommand,
        'LC_VERSION_MIN_IPHONEOS': VersionMinCommand,
        'LC_SOURCE_VERSION': SourceVersionCommand,
        'LC_MAIN': EntryPointCommand,
        'LC_CODE_SIGNATURE': LinkeditDataCommand,
        'LC_SEGMENT_SPLIT_INFO': LinkeditDataCommand,
        'LC_FUNCTION_STARTS': LinkeditDataCommand,
        'LC_DATA_IN_CODE': LinkeditDataCommand,
        'LC_DYLIB_CODE_SIGN_DRS': LinkeditDataCommand,
        'LC_LINKER_OPTIMIZATION_HINT': LinkeditDataCommand,
        'LC_UUID': UuidCommand,
        'LC_ID_DYLINKER': DylinkerCommand,
        'LC_LOAD_DYLINKER': DylinkerCommand,
        'LC_DYLD_ENVIRONMENT': DylinkerCommand,
        'LC_DYLD_INFO': DyldInfoCommand,
        'LC_DYLD_INFO_ONLY': DyldInfoCommand,
        'LC_SUB_FRAMEWORK': SubFrameworkCommand,
        'LC_SUB_CLIENTI': SubClientCommand,
        'LC_SUB_UMBRELLA': SubUmbrellaCommand,
        'LC_SUB_LIBRARY': SubLibraryCommand,
        'LC_PREBOUND_DYLIB': PreboundDylibCommand,
        'LC_TWOLEVEL_HINTS': TwolevelHintsCommand,
        'LC_PREBIND_CKSUM': PrebindCksumCommand,
        'LC_ENCRYPTION_INFO': EncryptionInfoCommand,
        'LC_LINKER_OPTION': LinkerOptionCommand,
    }
    # Load commands for 64-bit architectures
    COMMANDS_64 = {
        'LC_SEGMENT_64': SegmentCommand64,
        'LC_SYMTAB': SymtabCommand,
        'LC_DYSYMTAB': DysymtabCommand,
        'LC_LOAD_DYLIB': DylibCommand,
        'LC_LOAD_WEAK_DYLIB': DylibCommand,
        'LC_ID_DYLIB': DylibCommand,
        'LC_VERSION_MIN_MACOSX': VersionMinCommand,
        'LC_VERSION_MIN_IPHONEOS': VersionMinCommand,
        'LC_SOURCE_VERSION': SourceVersionCommand,
        'LC_MAIN': EntryPointCommand,
        'LC_CODE_SIGNATURE': LinkeditDataCommand,
        'LC_SEGMENT_SPLIT_INFO': LinkeditDataCommand,
        'LC_FUNCTION_STARTS': LinkeditDataCommand,
        'LC_DATA_IN_CODE': LinkeditDataCommand,
        'LC_DYLIB_CODE_SIGN_DRS': LinkeditDataCommand,
        'LC_LINKER_OPTIMIZATION_HINT': LinkeditDataCommand,
        'LC_UUID': UuidCommand,
        'LC_ID_DYLINKER': DylinkerCommand,
        'LC_LOAD_DYLINKER': DylinkerCommand,
        'LC_DYLD_ENVIRONMENT': DylinkerCommand,
        'LC_DYLD_INFO': DyldInfoCommand,
        'LC_DYLD_INFO_ONLY': DyldInfoCommand,
        'LC_SUB_FRAMEWORK': SubFrameworkCommand,
        'LC_SUB_CLIENTI': SubClientCommand,
        'LC_SUB_UMBRELLA': SubUmbrellaCommand,
        'LC_SUB_LIBRARY': SubLibraryCommand,
        'LC_PREBOUND_DYLIB': PreboundDylibCommand,
        'LC_TWOLEVEL_HINTS': TwolevelHintsCommand,
        'LC_PREBIND_CKSUM': PrebindCksumCommand,
        'LC_ENCRYPTION_INFO_64': EncryptionInfoCommand64,
        'LC_LINKER_OPTION': LinkerOptionCommand,
    }

    def __init__(self, mach_o_br):
        self.arch_width = None
        self.command_table = None
        self.mach_header = None
        self.load_commands = list()
        self.segments = dict()
        self.linkedit_br = None

        # Try to parse it as mach_header
        start = 0
        hdr_size = None
        try:
            hdr_size = MachHeader.get_size()
            self.mach_header = MachHeader(mach_o_br.bytes(start, hdr_size))
            self.arch_width = 32
            self.command_table = self.COMMANDS_32
        except HeaderInvalidValueError:
            pass

        # If fail, try mach_header_64
        if self.mach_header is None:
            try:
                hdr_size = MachHeader64.get_size()
                self.mach_header = MachHeader64(mach_o_br.bytes(start, hdr_size))
                self.arch_width = 64
                self.command_table = self.COMMANDS_64
            except ValueError:
                raise ValueError('mach_o: no valid mach header found')

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
                SectionParser(mach_o_br).parse(section_desc)

        # Add all segments
        for (seg_name, segment_desc) in self.segments.items():
            ProgressIndicator.display('parsing segment %s\n', seg_name)
            br = SegmentParser(mach_o_br).parse(segment_desc)
            if seg_name.startswith('__LINKEDIT'):
                self.linkedit_br = br

        ProgressIndicator.display('mach-o parsed\n')