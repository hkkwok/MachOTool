try:
    import Tkinter as Tk
    import ttk
except ImportError:
    import tkinter as Tk
    import tkinter.ttk as ttk

from tree_table import TreeTable
from window_tab import WindowTab
from utils.bytes_range import BytesRange
from mach_o.non_headers.section_block import CstringSection
from mach_o_helper import MachOHelper


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

        self.cstring_section_br = list()

    def clear(self):
        self.clear_ui()
        self.clear_states()

    def clear_states(self):
        self.bytes_range = None
        self.cstring_section_br = list()

    def clear_ui(self):
        self.table.clear()

    def load(self, bytes_range, bytes_):
        assert isinstance(bytes_range, BytesRange)

        def is_cstring_section(br, start, stop, level):
            assert start is not None and stop is not None and level is not None  # for get rid of pycharm warning
            if isinstance(br.data, CstringSection):
                return br
            return None

        self.cstring_section_br = bytes_range.iterate(is_cstring_section)
        self.bytes_range = bytes_range
        self.display()

    def display(self, filter_pattern=None):
        cur_mach_o = MachOHelper()
        for br in self.cstring_section_br:
            cstring_sect = br.data
            cur_mach_o.update(br)
            string_idx = 0
            for (string, offset) in cstring_sect.items():
                if filter_pattern is not None and filter_pattern not in string:
                    continue  # if there is a filter pattern and the string does not match, skip it
                if cur_mach_o.should_add_id():
                    cur_mach_o_id = self.table.add('', cur_mach_o.index,
                                                   (format(cur_mach_o.abs_start, ','), 'MachO[%d]' % cur_mach_o.index))
                    self.table.tree.item(cur_mach_o_id, open=True)
                    cur_mach_o.add_id(cur_mach_o_id)

                if (string_idx % 2) == 0:
                    kwargs = dict()
                else:
                    kwargs = {'tag': self.LIGHT_BLUE_TAG_NAME}
                self.table.add(cur_mach_o.id, string_idx,
                               (format(offset + cur_mach_o.abs_start, ','), string), **kwargs)
                string_idx += 1

    def search(self, event):
        assert event is not None  # for getting rid of pycharm warning
        self.clear_ui()
        self.display(self.search_entry.get())
