import Tkinter as Tk
import ttk

from tree_table import TreeTable
from window_tab import WindowTab
from utils.byte_range import ByteRange
from mach_o.headers.mach_header import MachHeader, MachHeader64
from mach_o.non_headers.section_block import CstringSection, ObjCMethodNameSection


class StringWindow(WindowTab):
    TITLE = 'Strings'
    LIGHT_BLUE_TAG_NAME = 'light_blue_background'

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

        self.table = TreeTable(self, 'String', columns=('Offset', 'String'))
        self.table.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=True)
        self.table.tree.tag_configure(self.LIGHT_BLUE_TAG_NAME, background='#e0e8f0')

        self.string_sections = list()
        self.mach_o = list()

    def clear(self):
        self.clear_ui()
        self.clear_states()

    def clear_states(self):
        self.byte_range = None
        self.string_sections = list()
        self.mach_o = list()

    def clear_ui(self):
        self.table.clear()

    def load(self, byte_range, bytes_):
        assert isinstance(byte_range, ByteRange)
        self.clear_states()
        byte_range.iterate(self._parse)
        self.byte_range = byte_range
        self.display()

    def _parse(self, br, start, stop, level):
        assert start is not None and stop is not None and level is not None
        if isinstance(br.data, (MachHeader, MachHeader64)):
            self.string_sections.append(list())
            self.mach_o.append(br)
        elif isinstance(br.data, (CstringSection, ObjCMethodNameSection)):
            assert len(self.string_sections) > 0
            self.string_sections[-1].append(br)

    def display(self, filter_pattern=None):
        mach_o_idx = 0
        for (n, mach_o) in enumerate(self.mach_o):
            mach_o_hdr = mach_o.data
            assert isinstance(mach_o_hdr, (MachHeader, MachHeader64))
            cpu_type = mach_o_hdr.FIELDS[1].display(mach_o_hdr)
            mach_o_id = self.table.add('', mach_o_idx, (format(mach_o.abs_start(), ','), 'Mach-O: %s' % cpu_type))
            str_sect_idx = 0
            for str_sect_br in self.string_sections[n]:
                cur_abs_start = str_sect_br.abs_start()
                string_sect = str_sect_br.data
                string_sect_desc = '%s, %s' % (string_sect.seg_name, string_sect.sect_name)
                sect_id = self.table.add(mach_o_id, str_sect_idx,
                                         (format(str_sect_br.abs_start(), ','), string_sect_desc))
                string_idx = 0
                for (string, offset) in string_sect.items():
                    if filter_pattern is not None and filter_pattern not in string:
                        continue  # if there is a filter pattern and the string does not match, skip it
                    if (string_idx % 2) == 0:
                        kwargs = dict()
                    else:
                        kwargs = {'tag': self.LIGHT_BLUE_TAG_NAME}
                    self.table.add(sect_id, string_idx,
                                   (format(offset + cur_abs_start, ','), string), **kwargs)
                    string_idx += 1

                # If there is no matching items in this string section, remove it
                if string_idx == 0:
                    self.table.tree.delete(sect_id)
                else:
                    self.table.tree.item(sect_id, open=True)
                    str_sect_idx += 1
            if str_sect_idx == 0:
                self.table.tree.delete(mach_o_id)
            else:
                self.table.tree.item(mach_o_id, open=True)
                mach_o_idx += 1

    def search(self, event):
        assert event is not None  # for getting rid of pycharm warning
        self.clear_ui()
        self.display(self.search_entry.get())
