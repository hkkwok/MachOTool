import Tkinter as Tk
import ttk

from tree_table import TreeTable
from light_table import LightTable
from window_tab import WindowTab
from utils.byte_range import ByteRange
from utils.commafy import commafy
from mach_o.headers.mach_header import MachHeader, MachHeader64
from mach_o.non_headers.section_block import CstringSection, ObjCMethodNameSection, NullTerminatedStringSection


class StringWindow(WindowTab):
    TITLE = 'Strings'
    LIGHT_BLUE_TAG_NAME = 'light_blue_background'
    LIGHT_BLUE = '#e0e8f0'
    MACH_O_TABLE_COLUMNS = ('Description', 'Offset', '# Strings', '# Matched')

    def __init__(self, parent):
        WindowTab.__init__(self, parent)
        self.search_bar = ttk.Labelframe(self, text='Filter', borderwidth=5)
        self.search_bar.pack(side=Tk.TOP, fill=Tk.X, expand=False)
        self.search_label = Tk.Label(self.search_bar, text='Pattern')
        self.search_label.pack(side=Tk.LEFT)

        self.gap = ttk.Frame(self, height=15)
        self.gap.pack(side=Tk.TOP, fill=Tk.X, expand=False)

        self.search_entry = Tk.Entry(self.search_bar)
        self.search_entry.pack(side=Tk.LEFT, fill=Tk.X, expand=True)
        self.search_entry.bind('<Return>', self.search)

        self.panedwindow = ttk.Panedwindow(self, orient=Tk.VERTICAL)
        self.panedwindow.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=True)

        self.mach_o_table = TreeTable(self, 'Mach-O / Sections', columns=self.MACH_O_TABLE_COLUMNS)
        self.mach_o_table.tree.configure(selectmode='browse')
        self.mach_o_table.tree.column(self.MACH_O_TABLE_COLUMNS[1], anchor=Tk.E)
        self.mach_o_table.tree.column(self.MACH_O_TABLE_COLUMNS[2], anchor=Tk.E)
        self.mach_o_table.tree.column(self.MACH_O_TABLE_COLUMNS[3], anchor=Tk.E)
        self.mach_o_table.select_callback = self._mach_o_selected
        self.panedwindow.add(self.mach_o_table)

        self.string_table = StringTableView(self)
        self.string_table.widget.tag_configure(self.LIGHT_BLUE_TAG_NAME, background=self.LIGHT_BLUE)
        self.panedwindow.add(self.string_table)

        self._mach_o_info = list()
        self._filter_mapping = None

    def clear(self):
        self.clear_ui()
        self.clear_states()

    def clear_states(self):
        self.byte_range = None
        self._mach_o_info = list()
        self._filter_mapping = None

    def clear_ui(self):
        self.mach_o_table.clear()
        self.string_table.clear_widget()

    def load(self, byte_range, bytes_):
        assert isinstance(byte_range, ByteRange)
        self.clear_states()
        byte_range.iterate(self._parse)
        self.byte_range = byte_range
        self.display()

    def _parse(self, br, start, stop, level):
        assert start is not None and stop is not None and level is not None
        if isinstance(br.data, (MachHeader, MachHeader64)):
            mach_o_hdr = br.data
            cpu_type = mach_o_hdr.FIELDS[1].display(mach_o_hdr)
            self._mach_o_info.append(_MachOInfo('Mach-O: ' + cpu_type, br.abs_start()))
        elif isinstance(br.data, (CstringSection, ObjCMethodNameSection)):
            assert len(self._mach_o_info) > 0
            section = br.data
            self._mach_o_info[-1].add_section('', section, br.abs_start())

    def display(self):
        filter_pattern = self.search_entry.get()

        # Update Mach-O table
        self._filter_mapping = dict()
        first_matched_id = None
        mach_o_idx = 0
        for mach_o_info in self._mach_o_info:
            # TODO - Add graphical progress indicator as this operation can be time consuming
            num_matches = mach_o_info.filter(filter_pattern)
            if num_matches == 0:
                continue
            mach_o_id = '.' + str(mach_o_idx)
            self.mach_o_table.add('', mach_o_idx,
                                  (mach_o_info.desc, commafy(mach_o_info.offset),
                                   commafy(mach_o_info.num_strings), commafy(mach_o_info.num_matched)))
            mach_o_idx += 1
            if first_matched_id is None:
                first_matched_id = mach_o_id
            self._filter_mapping[mach_o_id] = mach_o_info.string_sections

            section_idx = 0
            for sect_info in mach_o_info.string_sections:
                if sect_info.num_matched == 0:
                    continue
                sect_id = self.mach_o_table.add(mach_o_id, section_idx,
                                                (sect_info.desc, commafy(sect_info.offset),
                                                 commafy(sect_info.num_strings), commafy(sect_info.num_matched)))
                section_idx += 1
                self._filter_mapping[sect_id] = [sect_info]
            self.mach_o_table.tree.item(mach_o_id, open=True)

        # Update symbol table
        if first_matched_id is not None:
            self.mach_o_table.tree.selection_set(first_matched_id)

    def search(self, event):
        assert event is not None  # for getting rid of pycharm warning
        self.clear_ui()
        self.display()

    def _mach_o_selected(self, path):
        """
        When an item in the Mach-O table is clicked, we set one of a list of section to the
        string table for display.
        :param path:
        :return:
        """
        id_ = '.' + '.'.join([str(x) for x in path])
        sections = self._filter_mapping[id_]
        self.string_table.set_sections(sections)
        self.string_table.refresh()


class StringTableView(LightTable):
    COLUMNS = ('Offset', 'String')

    def __init__(self, parent):
        LightTable.__init__(self, parent, 'Strings', self.COLUMNS)
        self.widget.column('#0', anchor=Tk.E)
        self.widget.configure(selectmode='none')
        self._sections = None
        self.filter_pattern = None

    def data(self, data_row):
        for sect in self._sections:
            if data_row >= sect.num_matched:
                data_row -= sect.num_matched
                continue
            offset, string = sect.string(data_row)
            return commafy(offset), string
        assert False  # should never get here

    def set_sections(self, sections):
        assert isinstance(sections, list)
        self._sections = sections
        num_matched = sum([sect.num_matched for sect in self._sections])
        self.set_rows(num_matched)


class _MachOInfo(object):
    def __init__(self, desc, offset):
        self.desc = desc
        self.offset = offset
        self.string_sections = list()
        self.num_matched = 0
        self.num_strings = 0

    def add_section(self, seg_name, section, offset):
        assert isinstance(section, NullTerminatedStringSection)
        desc = '%s, %s' % (seg_name, section.sect_name)
        section_info = _StringSectionInfo(desc, offset, section)
        self.string_sections.append(section_info)
        self.num_strings += section.num_strings()

    def filter(self, pattern):
        self.num_matched = sum([sect.filter(pattern) for sect in self.string_sections])
        return self.num_matched


class _StringSectionInfo(object):
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
