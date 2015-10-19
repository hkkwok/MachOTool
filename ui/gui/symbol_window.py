try:
    import Tkinter as Tk
    import ttk
except ImportError:
    import _tkinter as Tk
    import tkinter.ttk as ttk
from window_tab import WindowTab
from tree_table import TreeTable
from utils.byte_range import ByteRange
from utils.header import NullTerminatedStringField
from mach_o.headers.nlist import Nlist64
from mach_o.headers.section import Section, Section64
from mach_o.non_headers.symbol_table_block import SymbolTableBlock
from mach_o.headers.mach_header import MachHeader, MachHeader64


class SymbolWindow(WindowTab):
    TITLE = 'Symbols'
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

        self.table = TreeTable(self, 'String',
                               columns=('Index', 'Section', 'Type', 'Global', 'Defined', 'Lazy', 'Symbol'))
        self.table.tree.column('Type', width=65, stretch=False, anchor=Tk.CENTER)
        self.table.tree.column('Global', width=45, stretch=False, anchor=Tk.CENTER)
        self.table.tree.column('Defined', width=45, stretch=False, anchor=Tk.CENTER)
        self.table.tree.column('Lazy', width=45, stretch=False, anchor=Tk.CENTER)
        self.table.tree.tag_configure(self.LIGHT_BLUE_TAG_NAME, background='#e0e8f0')
        self.table.pack(side=Tk.BOTTOM, fill=Tk.BOTH, expand=True)

        # symbol_tables is a list of OrderedDict. One OrderedDict per Mach-O. In each
        # OrderedDict, symbol table strings are keyed by offset (from the beginning of
        # the symbol table string table region.
        self.symbol_tables = list()
        self.mach_o = list()
        self.sections = [None]

    def clear(self):
        self.clear_ui()
        self.clear_states()

    def clear_ui(self):
        self.table.clear()

    def clear_states(self):
        self.byte_range = None
        self.symbol_tables = list()
        self.mach_o = list()

    def load(self, byte_range, bytes_):
        assert isinstance(byte_range, ByteRange)
        self.symbol_tables = list()
        byte_range.iterate(self._parse)
        self.byte_range = byte_range
        self.display()

    def _parse(self, br, start, stop, level):
        assert start is not None and stop is not None and level is not None  # get rid of pycharm warnings
        if isinstance(br.data, (MachHeader, MachHeader64)):
            self.mach_o.append(br.data)
            self.symbol_tables.append(list())
        elif isinstance(br.data, SymbolTableBlock):
            self.symbol_tables[-1].append(br.data)
        elif isinstance(br.data, (Section, Section64)):
            self.sections.append(br.data)

    @staticmethod
    def _y_or_n(boolean):
        if boolean:
            return 'Y'
        else:
            return 'N'

    def display(self):
        filter_pattern = self.search_entry.get()

        mach_o_idx = 0
        for symbol_table_list in self.symbol_tables:
            mach_o_hdr = self.mach_o[mach_o_idx]
            cpu_type = mach_o_hdr.FIELDS[1].display(mach_o_hdr)
            mach_o_id = self.table.add('', mach_o_idx, ('Mach-O', cpu_type, '', '', '', '', ''))
            symbol_idx = 0
            for symbol_table in symbol_table_list:
                for (index, n_strx, n_type, n_sect, n_desc, n_value, symbol_name) in symbol_table.symbols:
                    if filter_pattern not in symbol_name:
                        continue
                    symbol = Nlist64(index=index,
                                     n_strx=n_strx,
                                     n_type=n_type,
                                     n_sect=n_sect,
                                     n_desc=n_desc,
                                     n_value=n_value)
                    if (symbol_idx % 2) == 0:
                        kwargs = dict()
                    else:
                        kwargs = {'tag': self.LIGHT_BLUE_TAG_NAME}
                    if symbol.n_sect == 0:
                        section_desc = ''
                    else:
                        this_section = self.sections[symbol.n_sect]
                        section_desc = '%s, %s' % \
                                       (NullTerminatedStringField.get_string(this_section.segname),
                                        NullTerminatedStringField.get_string(this_section.sectname))
                    self.table.add(mach_o_id, symbol_idx,
                                   (str(symbol.index),
                                    section_desc,
                                    symbol.type(),
                                    self._y_or_n(symbol.is_global()),
                                    self._y_or_n(symbol.is_defined()),
                                    self._y_or_n(symbol.is_lazy()),
                                    symbol_name), **kwargs)
                    symbol_idx += 1
            if len(self.table.tree.get_children(mach_o_id)) == 0:
                self.table.tree.delete(mach_o_id)
            else:
                self.table.tree.item(mach_o_id, open=True)
            mach_o_idx += 1

    def search(self, event):
        assert event is not None
        self.clear_ui()
        self.display()
