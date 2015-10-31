import Tkinter as Tk
import ttk
from window_tab import WindowTab
from tree_table import TreeTable
from utils.byte_range import ByteRange
from utils.commafy import commafy
from mach_o.headers.section import Section, Section64
from mach_o.non_headers.symbol_table_block import SymbolTable
from mach_o.headers.mach_header import MachHeader, MachHeader64
from mach_o.non_headers.symbol_info import SymbolMachOInfo
from light_table import LightTable


class SymbolWindow(WindowTab):
    TITLE = 'Symbols'
    LIGHT_BLUE_TAG_NAME = 'light_blue_background'
    LIGHT_BLUE = '#e0e8f0'
    MACH_O_TABLE_COLUMNS = ('CPU Type', '# Symbols', '# Matched')

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

        self.mach_o_table = TreeTable(self, 'Mach-O', columns=self.MACH_O_TABLE_COLUMNS)
        self.mach_o_table.tree.configure(selectmode='browse')
        self.mach_o_table.tree.column(self.MACH_O_TABLE_COLUMNS[1], width=75, stretch=False, anchor=Tk.E)
        self.mach_o_table.tree.column(self.MACH_O_TABLE_COLUMNS[2], width=75, stretch=False, anchor=Tk.E)
        self.mach_o_table.tree.tag_configure(self.LIGHT_BLUE_TAG_NAME, background=self.LIGHT_BLUE)
        self.mach_o_table.select_callback = self._mach_o_selected
        self.panedwindow.add(self.mach_o_table)

        self.symbol_table = SymbolTableView(self)
        self.panedwindow.add(self.symbol_table)

        self._mach_o_info = list()
        self._filter_mapping = None  # map table index to mach-o info index when an entry in mach-o table is clicked

    def clear(self):
        self.clear_ui()
        self.clear_states()

    def clear_ui(self):
        self.mach_o_table.clear()
        self.symbol_table.clear_widget()

    def clear_states(self):
        self.byte_range = None
        self._mach_o_info = list()
        self._filter_mapping = None

    def load(self, byte_range, bytes_):
        assert isinstance(byte_range, ByteRange)
        byte_range.iterate(self._parse)
        self.byte_range = byte_range
        self.display()

    def _parse(self, br, start, stop, level):
        assert start is not None and stop is not None and level is not None  # get rid of pycharm warnings
        if isinstance(br.data, (MachHeader, MachHeader64)):
            mach_o_hdr = br.data
            cpu_type = mach_o_hdr.FIELDS[1].display(mach_o_hdr)
            mach_o_info = SymbolMachOInfo(cpu_type)
            self._mach_o_info.append(mach_o_info)
        elif isinstance(br.data, SymbolTable):
            self._mach_o_info[-1].add_symbol_table(br.data)
        elif isinstance(br.data, (Section, Section64)):
            self._mach_o_info[-1].add_section(br.data)

    def display(self):
        filter_pattern = self.search_entry.get()

        # Update Mach-O table
        self._filter_mapping = list()
        for (mach_o_idx, mach_o_info) in enumerate(self._mach_o_info):
            # TODO - Add graphical progress indicator as this operation can be time consuming
            num_matches = mach_o_info.filter(filter_pattern)
            if num_matches == 0:
                continue
            self.mach_o_table.add('', len(self._filter_mapping),
                                  (mach_o_info.desc, commafy(mach_o_info.num_symbols()),
                                   commafy(mach_o_info.num_matched)))
            self._filter_mapping.append(mach_o_idx)

        # Update symbol table
        if len(self._filter_mapping) > 0:
            self.mach_o_table.tree.selection_set('.0')

    def search(self, event):
        assert event is not None
        self.clear_ui()
        self.display()

    def _mach_o_selected(self, path):
        assert len(path) == 1  # a flat list should only return a length-1 list
        mach_o = self._mach_o_info[path[0]]
        self.symbol_table.set_mach_o_info(mach_o)
        self.symbol_table.refresh()


class SymbolTableView(LightTable):
    COLUMNS = ('Index', 'Section', 'Type', 'Global', 'Defined', 'Lazy', 'Symbol')
    LIGHT_BLUE_TAG_NAME = 'light_blue_background'
    LIGHT_BLUE = '#e0e8f0'

    def __init__(self, parent):
        LightTable.__init__(self, parent, 'Symbols', self.COLUMNS)
        self.widget.column('#0', anchor=Tk.W)
        self.widget.column(self.COLUMNS[2], width=65, stretch=False, anchor=Tk.CENTER)
        self.widget.column(self.COLUMNS[3], width=45, stretch=False, anchor=Tk.CENTER)
        self.widget.column(self.COLUMNS[4], width=45, stretch=False, anchor=Tk.CENTER)
        self.widget.column(self.COLUMNS[5], width=45, stretch=False, anchor=Tk.CENTER)
        self.widget.tag_configure(self.LIGHT_BLUE_TAG_NAME, background=self.LIGHT_BLUE)
        self.widget.configure(selectmode='none')
        self._mach_o_info = None
        self.filter_pattern = None

    def data(self, data_row):
        symbol, symbol_name, section_desc = self._mach_o_info.symbol(data_row)
        return (str(symbol.index),
                section_desc,
                symbol.type(),
                self._y_or_n(symbol.is_global()),
                self._y_or_n(symbol.is_defined()),
                self._y_or_n(symbol.is_lazy()),
                symbol_name)

    def set_mach_o_info(self, mach_o_info):
        self._mach_o_info = mach_o_info
        self.set_rows(self._mach_o_info.num_matched)

    @staticmethod
    def _y_or_n(boolean):
        if boolean:
            return 'Y'
        else:
            return 'N'
