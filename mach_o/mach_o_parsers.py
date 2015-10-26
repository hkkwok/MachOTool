from utils.byte_range_parser import ByteRangeParser
from utils.unescape import Unescape
from utils.progress_indicator import ProgressIndicator
from utils.header import NullTerminatedStringField
from utils.range import Range

from headers.lc_str import LcStr
from headers.load_command import LoadCommandCommand, LoadCommand
from headers.segment_command import SegmentCommand, SegmentCommand64
from headers.dylib_command import DylibCommand
from headers.section import Section, Section64
from headers.dylinker_command import DylinkerCommand
from headers.dyld_info_command import DyldInfoCommand
from headers.symtab_command import SymtabCommand
from headers.dysymtab_command import DysymtabCommand
from headers.sub_library_command import SubLibraryCommand
from headers.sub_framework_command import SubFrameworkCommand
from headers.sub_client_command import SubClientCommand
from headers.sub_umbrella_command import SubUmbrellaCommand
from headers.prebound_dylib_command import PreboundDylibCommand
from headers.linkedit_data_command import LinkeditDataCommand
from headers.twolevel_hints_command import TwolevelHintsCommand
from headers.prebind_cksum_command import PrebindCksumCommand
from headers.encryption_info_command import EncryptionInfoCommand, EncryptionInfoCommand64
from headers.linker_option_command import LinkerOptionCommand
from headers.nlist import Nlist, Nlist64
from headers.indirect_symbol import IndirectSymbol
from headers.rpath_command import RpathCommand

from non_headers.padding import UnexpectedPadding, Padding
from non_headers.load_command_block import LoadCommandBlock
from non_headers.segment_block import SegmentBlock
from non_headers.section_block import SectionBlock, DataSection, TextSection, CstringSection, ObjCMethodNameSection
from non_headers.cstring import Cstring, ObjCMethodName
from non_headers.linkedit_data import LinkEditData
from non_headers.symbol_table_block import SymbolTable, SymbolStringTable
from non_headers.symbol_table_block import IndirectSymbolTable, ExtRefSymbolTable


class SegmentDescriptor(object):
    def __init__(self, segment_command):
        assert isinstance(segment_command, (SegmentCommand, SegmentCommand64))
        self.segment_command = segment_command
        self.name = self.segment_command.segname
        self.sections = dict()

    def add_section(self, section):
        assert isinstance(section, (Section, Section64))
        section_desc = SectionDescriptor(section)
        self.sections[section_desc.name] = section_desc


class SectionDescriptor(object):
    SEG_PAGEZERO = '__PAGEZERO'
    SEG_TEXT = '__TEXT'
    SEG_DATA = '__DATA'

    SECT_BSS = '__bss'
    SECT_COMMON = '__common'
    SECT_CSTRING = '__cstring'  # This is not in loader.h but added anyway
    SECT_OBJC_METHNAME = '__objc_methname'

    def __init__(self, section):
        assert isinstance(section, (Section, Section64))
        self.section = section
        self.name = section.sectname

    def is_section(self, seg_name, sect_name):
        section = self.section
        return section.segname.startswith(seg_name) and section.sectname.startswith(sect_name)

    def is_text_section(self, sect_name):
        return self.is_section(self.SEG_TEXT, sect_name)

    def is_data_section(self, sect_name):
        return self.is_section(self.SEG_DATA, sect_name)

    def is_cstring(self):
        return self.is_text_section(self.SECT_CSTRING)

    def is_bss(self):
        return self.is_data_section(self.SECT_BSS)

    def is_common(self):
        return self.is_data_section(self.SECT_COMMON)

    def is_objc_methname(self):
        return self.is_text_section(self.SECT_OBJC_METHNAME)


class LoadCommandParser(ByteRangeParser):
    def __init__(self, byte_range, mach_o):
        super(LoadCommandParser, self).__init__(byte_range)
        self.mach_o = mach_o

        self.lc = None
        self.hdr_size = None

    def _add_lc_str(self, name, offset):
        self._add_padding(UnexpectedPadding('unexpected gap'), offset)
        lc_str = LcStr.find_str(name, self._get_bytes())
        self.add_subrange(lc_str, len(lc_str))

    def _add_alignment_padding(self):
        self._add_padding(Padding('alignment'))

    def parse(self, generic_lc, start):
        self.initialize(start, generic_lc.cmdsize)

        # Try to create a specific LC object for the header
        cmd_desc = LoadCommandCommand.get_desc(generic_lc.cmd)
        cmd_class = self.mach_o.command_table.get(cmd_desc, None)
        lc = None
        if cmd_class is not None:
            self.hdr_size = cmd_class.get_size()
            assert callable(cmd_class)
            lc = cmd_class(self._get_bytes(self.hdr_size))
        if cmd_class is None or lc is None:
            # This is an unknown LC. We can only create a generic LC byte range and a unknown padding.
            hdr_size = LoadCommand.get_size()
            self.add_subrange(generic_lc, hdr_size)
            self.add_subrange(UnexpectedPadding('unknown LC'), self.cmd_size - hdr_size)
            return
        self.add_subrange(lc, self.hdr_size)

        # Handle each specific LC
        if cmd_desc in ('LC_SEGMENT', 'LC_SEGMENT_64'):
            assert isinstance(lc, (SegmentCommand, SegmentCommand64))
            segment_desc = SegmentDescriptor(lc)
            self.mach_o.segments[segment_desc.name] = segment_desc
            for idx in xrange(lc.nsects):
                # ???? Should be possible to miss 32 and 64-bit sections, right? If yes, can move this loop outside
                if cmd_desc == 'LC_SEGMENT':
                    cls = Section
                elif cmd_desc == 'LC_SEGMENT_64':
                    cls = Section64
                else:
                    assert False
                cls_size = cls.get_size()
                assert callable(cls)
                section = cls(self._get_bytes(cls_size))
                self.add_subrange(section, cls_size)
                segment_desc.add_section(section)
            if lc.nsects > 0:
                self.add_subrange_beneath(LoadCommandBlock(cmd_desc), self.cmd_size)
        elif cmd_desc == 'LC_LOAD_DYLIB':
            assert isinstance(lc, DylibCommand)
            self._add_lc_str('dylib_name', lc.dylib_name_offset)  # parse dylib.name
            self._add_alignment_padding()
            self.byte_range.insert_subrange(self.start, self.cmd_size,
                                            data=LoadCommandBlock(cmd_desc))
        elif cmd_desc in ('LC_ID_DYLINKER', 'LC_LOAD_DYLINKER', 'LC_DYLD_ENVIRONMENT'):
            assert isinstance(lc, DylinkerCommand)
            self._add_lc_str('name', lc.name_offset)  # parse name
            self._add_alignment_padding()
            self.byte_range.insert_subrange(self.start, self.cmd_size,
                                            data=LoadCommandBlock(cmd_desc))
        elif cmd_desc in ('LC_DYLD_INFO', 'LC_DYLD_INFO_ONLY'):
            assert isinstance(lc, DyldInfoCommand)
            # Record the rebase, different types of bind and export sections
            DyldInfoParser(self.byte_range, self.mach_o.arch_width).parse(lc)
        elif cmd_desc == 'LC_SYMTAB':
            assert isinstance(lc, SymtabCommand)
            SymtabParser(self.byte_range, self.mach_o).parse(lc)
        elif cmd_desc == 'LC_DYSYMTAB':
            assert isinstance(lc, DysymtabCommand)
            DysymtabParser(self.byte_range, self.mach_o.arch_width).parse(lc)
        elif cmd_desc in ('LC_FUNCTION_STARTS', 'LC_DATA_IN_CODE', 'LC_DYLIB_CODE_SIGN_DRS', 'LC_CODE_SIGNATURE'):
            assert isinstance(lc, LinkeditDataCommand)
            LinkeditDataParser(self.byte_range, self.mach_o.arch_width).parse(lc)
        elif cmd_desc == 'LC_SUB_FRAMEWORK':
            assert isinstance(lc, SubFrameworkCommand)
            self._add_lc_str('umbrella', lc.umbrella_offset)
            self._add_alignment_padding()
            self.byte_range.insert_subrange(self.start, self.cmd_size,
                                            data=LoadCommandBlock(cmd_desc))
        elif cmd_desc == 'LC_SUB_CLIENT':
            assert isinstance(lc, SubClientCommand)
            self._add_lc_str('client', lc.client_offset)
            self._add_alignment_padding()
            self.byte_range.insert_subrange(self.start, self.cmd_size,
                                            data=LoadCommandBlock(cmd_desc))
        elif cmd_desc == 'LC_SUB_UMBRELLA':
            assert isinstance(lc, SubUmbrellaCommand)
            self._add_lc_str('sub_umbrella', lc.sub_umbrella_offset)
            self._add_alignment_padding()
            self.byte_range.insert_subrange(self.start, self.cmd_size,
                                            data=LoadCommandBlock(cmd_desc))
        elif cmd_desc == 'LC_SUB_LIBRARY':
            assert isinstance(lc, SubLibraryCommand)
            self._add_lc_str('library', lc.library_offset)
            self._add_alignment_padding()
            self.byte_range.insert_subrange(self.start, self.cmd_size,
                                            data=LoadCommandBlock(cmd_desc))
        elif cmd_desc == 'LC_PREBOUND_DYLIB':
            assert isinstance(lc, PreboundDylibCommand)
            self._add_lc_str('name', lc.name_offset)
            self._add_padding(UnexpectedPadding('unexpected gap'), lc.linked_modules_offset)
            # get the module bit vector
            num_bytes = (lc.nmodules + 7) / 8
            bit_vector = self._get_bytes(num_bytes)
            self.add_subrange('<modules:%s>' % ' '.join(['%02x' % x for x in bit_vector]))
            self._add_alignment_padding()
            self.byte_range.insert_subrange(self.start, self.cmd_size,
                                            data=LoadCommandBlock(cmd_desc))
        elif cmd_desc == 'LC_TWOLEVEL_HINTS':
            assert isinstance(lc, TwolevelHintsCommand)
            raise NotImplementedError()  # TODO - need to make a test binary
        elif cmd_desc == 'LC_PREBIND_CKSUM':
            assert isinstance(lc, PrebindCksumCommand)
            raise NotImplementedError()  # TODO - need to make a test binary
        elif cmd_desc in ('LC_ENCRYPTION_INFO', 'LC_ENCRYPTION_INFO_64'):
            assert isinstance(lc, (EncryptionInfoCommand, EncryptionInfoCommand64))
            # We need to delay the creation of an encrypted block because it usually
            # overlaps with multiple text sections. If we add it now, it will
            # causes an exception when other sections are added. So, we save it for now
            # and process it after all sections are created but before segments are
            # created.
            self.mach_o.encryption_info_commands.append(lc)
        elif cmd_desc == 'LC_LINKER_OPTION':
            assert isinstance(lc, LinkerOptionCommand)
            raise NotImplementedError()  # TODO - need to make a test binary
        elif cmd_desc == 'LC_RPATH':
            assert isinstance(lc, RpathCommand)
            self._add_lc_str('path', lc.path_offset)
            self._add_alignment_padding()
            self.byte_range.insert_subrange(self.start, self.cmd_size,
                                            data=LoadCommandBlock(cmd_desc))

        # Account for any trailing gap
        self._add_padding(Padding(cmd_desc))


class SectionParser(ByteRangeParser):
    def __init__(self, mach_o_br, mach_o):
        super(SectionParser, self).__init__(mach_o_br)
        self.mach_o = mach_o

    def parse(self, section_desc):
        section = section_desc.section
        self.initialize(section.offset, section.size)

        # Get the segment and section names
        seg_name = NullTerminatedStringField.get_string(section.segname)
        sect_name = NullTerminatedStringField.get_string(section.sectname)
        bytes_ = self._get_bytes()
        if seg_name == '__TEXT':
            data_section = TextSection(sect_name, bytes_)
        elif seg_name == '__DATA':
            data_section = DataSection(sect_name, bytes_)
        else:
            data_section = SectionBlock(seg_name, sect_name, bytes_)

        # If the section is inside a encrypted region (specificed by LC_ENCRYPTION_INFO),
        # we cannot parse it because we don't have the decryption key. So, we just
        # create a block without trying to parse its content.
        if self.mach_o.is_section_encrypted(section):
            data_section.name += ' [ENCRYPTED]'
            self.add_subrange(data_section, section.size)
            return

        if section.offset == 0:
            # .bss and .common sections only exist in VM but not in the file. So, they have an offset of 0
            # which aliases with the mach header. We do not add any subrange for these sections since
            # there is no data to parse / display.

            # TODO - in some iOS binraries, offset is set to 0 for many sections that should have data
            # Need to study them more to determine if offset is just not set proerly and we can
            # compute the offset from the first data section and the VM address.
            return
        elif section_desc.is_cstring():
            data_section = CstringSection(bytes_)
            cstring_br = self.add_subrange(data_section, section.size)
            for (offset, string) in data_section.items():
                unescaped_string = Unescape.convert(string)
                cstring_br.add_subrange(offset, len(string) + 1, data=Cstring(unescaped_string))
        elif section_desc.is_objc_methname():
            data_section = ObjCMethodNameSection(bytes_)
            obj_methname_br = self.add_subrange(data_section, section.size)
            for (offset, string) in data_section.items():
                unescaped_string = Unescape.convert(string)
                obj_methname_br.add_subrange(offset, len(string) + 1, data=ObjCMethodName(unescaped_string))
        else:
            self.add_subrange(data_section, section.size)


class SegmentParser(ByteRangeParser):
    def __init__(self, mach_o_br):
        super(SegmentParser, self).__init__(mach_o_br)

    def parse(self, segment_desc):
        segment_command = segment_desc.segment_command
        assert isinstance(segment_command, (SegmentCommand, SegmentCommand64))
        self.initialize(segment_command.fileoff, segment_command.filesize)

        segment = SegmentBlock(segment_desc.name)
        br = self.add_subrange_beneath(segment)

        # Mark all remaining gaps
        br.scan_gap(lambda start, stop: UnexpectedPadding('unused segment data'))

        return br


class LinkEditParser(ByteRangeParser):
    def __init__(self, linkedit_br, mach_o):
        super(LinkEditParser, self).__init__(linkedit_br)
        self.mach_o = mach_o

    def add_section(self, abs_off, length, data=None):
        if length == 0:
            return None
        self.current = abs_off
        return self.add_subrange(data, length)


class DyldInfoParser(LinkEditParser):
    def __init__(self, linkedit_br, mach_o):
        super(DyldInfoParser, self).__init__(linkedit_br, mach_o)

    def parse(self, dyld_info_command):
        if dyld_info_command is None:
            return
        self.initialize(0, len(self.byte_range))
        self.add_section(dyld_info_command.rebase_off, dyld_info_command.rebase_size,
                         data=LinkEditData('rebase section'))
        self.add_section(dyld_info_command.bind_off, dyld_info_command.bind_size,
                         data=LinkEditData('bind section'))
        self.add_section(dyld_info_command.weak_bind_off, dyld_info_command.weak_bind_size,
                         data=LinkEditData('weak bind section'))
        self.add_section(dyld_info_command.lazy_bind_off, dyld_info_command.lazy_bind_size,
                         data=LinkEditData('lazy bind section'))
        self.add_section(dyld_info_command.export_off, dyld_info_command.export_size,
                         data=LinkEditData('export section'))


class SymtabParser(LinkEditParser):
    def __init__(self, byte_range, mach_o):
        super(SymtabParser, self).__init__(byte_range, mach_o)
        if self.mach_o.arch_width == 32:
            self.nlist_class = Nlist
        elif self.mach_o.arch_width == 64:
            self.nlist_class = Nlist64
        else:
            raise ValueError()
        self.nlist_size = self.nlist_class.get_size()

    @staticmethod
    def _find_string(bytes_, start):
        cur = start
        while cur < len(bytes_) and bytes_[cur] != '\x00':
            cur += 1
        return bytes_[start:cur], cur - start + 1  # the 2nd value is total length that includes terminating NULL

    def parse(self, symtab_command):
        if symtab_command is None:
            return
        self.initialize(0, len(self.byte_range))
        if ProgressIndicator.ENABLED:
            progress = ProgressIndicator('parsing symbol table...', 4096)
        else:
            progress = None

        # Add nlist entries and string table section.
        sym_tab = SymbolTable(symtab_command.nsyms)
        sym_str_tab = SymbolStringTable()
        sym_br = self.add_section(symtab_command.symoff, symtab_command.nsyms * self.nlist_size, data=sym_tab)
        self.add_section(symtab_command.stroff, symtab_command.strsize, data=sym_str_tab)
        str_bytes_ = self.byte_range.bytes(symtab_command.stroff,
                                           symtab_command.stroff + symtab_command.strsize)

        # Parse all nlist entries
        for idx in xrange(symtab_command.nsyms):
            if progress is not None:
                progress.click()
            start = idx * self.nlist_size
            stop = start + self.nlist_size
            bytes_ = sym_br.bytes(start, stop)
            nlist = self.nlist_class(bytes_)
            # The original code was:
            #
            # sym_br.add_subrange(start, self.nlist_size, data=nlist)
            #
            # The problem is that for a real iOS app, there can be hundreds of thousands if not
            # millions of symbols and these Nlist and BytesRange objects consume a lot of memory.
            # (Each python object with attribute seems to consume at least 300B.)
            #
            # The solution is to deviate the framework and save the values of these nlist headers
            # into a big list.
            sym_tab.add(nlist)
            if nlist.n_strx == 0:
                # From nlist.h:
                #
                # Symbols with a index into the string table of zero (n_un.n_strx == 0) are
                # defined to have a null, "", name.  Therefore all string indexes to non null
                # names must not have a zero string index.  This is bit historical information
                # that has never been well documented.
                pass
            else:
                (sym_name, total_len) = self._find_string(str_bytes_, nlist.n_strx)
                # Original code is:
                #
                # str_br.add_subrange(nlist.n_strx, total_len, data=SymtabString(nlist.n_strx, sym_name))
                #
                # Again, we avoid creating the byte range in order to reduce memory consumption.
                sym_str_tab.add(nlist.n_strx, sym_name)
        sym_tab.correlate_string_table(sym_str_tab)
        if progress is not None:
            progress.done()


class DysymtabParser(LinkEditParser):
    def __init__(self, linkedit_br, mach_o):
        super(DysymtabParser, self).__init__(linkedit_br, mach_o)

    def parse(self, dysymtab_command):
        if dysymtab_command is None:
            return
        assert isinstance(dysymtab_command, DysymtabCommand)
        self.initialize(0, len(self.byte_range))
        self.add_section(dysymtab_command.extrefsymoff, dysymtab_command.nextrefsyms * 4,
                         data=ExtRefSymbolTable(dysymtab_command.nextrefsyms))
        indirect_sym_size = 4
        sym_br = self.add_section(dysymtab_command.indirectsymoff, dysymtab_command.nindirectsyms * indirect_sym_size,
                                  data=IndirectSymbolTable(dysymtab_command.nindirectsyms))
        # Parse all nlist entries
        for idx in xrange(dysymtab_command.nindirectsyms):
            start = idx * indirect_sym_size
            stop = start + indirect_sym_size
            bytes_ = sym_br.bytes(start, stop)
            indirect_sym = IndirectSymbol(bytes_)
            sym_br.add_subrange(start, indirect_sym_size, data=indirect_sym)

        # TODO - still need to parse table of content, module table, external and local relocation entries


class LinkeditDataParser(LinkEditParser):
    def __init__(self, linkedit_br, mach_o):
        super(LinkeditDataParser, self).__init__(linkedit_br, mach_o)

    def parse(self, linkedit_data_command):
        assert isinstance(linkedit_data_command, LinkeditDataCommand)
        self.initialize(0, len(self.byte_range))

        if linkedit_data_command.cmd == LoadCommandCommand.COMMANDS['LC_FUNCTION_STARTS']:
            desc = 'function starts'
        elif linkedit_data_command.cmd == LoadCommandCommand.COMMANDS['LC_DATA_IN_CODE']:
            desc = 'data in code'
        elif linkedit_data_command.cmd == LoadCommandCommand.COMMANDS['LC_DYLIB_CODE_SIGN_DRS']:
            desc = 'dylib code sign drs'
        elif linkedit_data_command.cmd == LoadCommandCommand.COMMANDS['LC_CODE_SIGNATURE']:
            desc = 'code signature'
        else:
            raise ValueError()
        self.add_section(linkedit_data_command.dataoff, linkedit_data_command.datasize,
                         data=LinkEditData(desc))
