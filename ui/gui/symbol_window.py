import Tkinter as Tk
import ttk
import tkFont
from window_tab import WindowTab
from tree_table import TreeTable
from utils.byte_range import ByteRange
from utils.header import NullTerminatedStringField
from mach_o.headers.nlist import Nlist64
from mach_o.headers.section import Section, Section64
from mach_o.non_headers.symbol_table_block import SymbolTable
from mach_o.headers.mach_header import MachHeader, MachHeader64
from light_scrollable import LightScrollableWidget


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
        self.mach_o_table.tree.column(self.MACH_O_TABLE_COLUMNS[1], width=75, stretch=False, anchor=Tk.E)
        self.mach_o_table.tree.column(self.MACH_O_TABLE_COLUMNS[2], width=75, stretch=False, anchor=Tk.E)
        self.mach_o_table.tree.tag_configure(self.LIGHT_BLUE_TAG_NAME, background=self.LIGHT_BLUE)
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
            mach_o_info = MachOInfo(cpu_type)
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
                                  (mach_o_info.desc, mach_o_info.num_symbols(), mach_o_info.num_matched))
            self._filter_mapping.append(mach_o_idx)

        # Update symbol table
        if len(self._filter_mapping) > 0:
            first_matched_mach_o = self._mach_o_info[self._filter_mapping[0]]
            self.symbol_table.set_mach_o_info(first_matched_mach_o)
            self.symbol_table.display()

    def search(self, event):
        assert event is not None
        self.clear_ui()
        self.display()


class SymbolTableView(LightScrollableWidget):
    COLUMNS = ('Index', 'Section', 'Type', 'Global', 'Defined', 'Lazy', 'Symbol')
    LIGHT_BLUE_TAG_NAME = 'light_blue_background'
    LIGHT_BLUE = '#e0e8f0'

    def __init__(self, parent):
        LightScrollableWidget.__init__(self, parent, 'Symbols',
                                       lambda p: ttk.Treeview(self, columns=self.COLUMNS[1:]))
        self.widget.heading('#0', text=self.COLUMNS[0])
        for col in self.COLUMNS[1:]:
            self.widget.heading(col, text=col)
        self.widget.column(self.COLUMNS[2], width=65, stretch=False, anchor=Tk.CENTER)
        self.widget.column(self.COLUMNS[3], width=45, stretch=False, anchor=Tk.CENTER)
        self.widget.column(self.COLUMNS[4], width=45, stretch=False, anchor=Tk.CENTER)
        self.widget.column(self.COLUMNS[5], width=45, stretch=False, anchor=Tk.CENTER)
        self.widget.tag_configure(self.LIGHT_BLUE_TAG_NAME, background=self.LIGHT_BLUE)

        self._mach_o_info = None
        self.filter_pattern = None

    def clear_widget(self):
        for child in self.widget.get_children():
            self.widget.delete(child)

    def row_height(self):
        font = tkFont.Font(font='TkDefaultFont')
        font_height = font.metrics('linespace')
        return font_height + 2

    def widget_rows(self):
        if self._widget_height is None:
            return self.widget.cget('height')
        return self._widget_height / self.row_height() - 2

    def show_row(self, data_row, view_row):
        symbol, symbol_name, section_desc = self._mach_o_info.symbol(data_row)
        if (data_row % 2) == 0:
            kwargs = dict()
        else:
            kwargs = {'tag': self.LIGHT_BLUE_TAG_NAME}
        child_id = '.' + str(view_row)
        print 'SHOW_ROW:', data_row, view_row, child_id, symbol_name
        self.widget.insert(parent='', index=view_row, iid=child_id, text=str(symbol.index),
                           values=(section_desc,
                                   symbol.type(),
                                   self._y_or_n(symbol.is_global()),
                                   self._y_or_n(symbol.is_defined()),
                                   self._y_or_n(symbol.is_lazy()),
                                   symbol_name),
                           **kwargs)

    def set_mach_o_info(self, mach_o_info):
        self._mach_o_info = mach_o_info
        self.rows = self._mach_o_info.num_matched

    def display(self):
        self.clear_widget()
        self._update_widget_rows(None, None)
        widget_rows = self.widget_rows()
        if self.rows <= widget_rows:
            self._show(0, self.rows - 1)
            self.yscroll.set('0.0', '1.0')
        else:
            self._show(0, widget_rows - 1)
            self.yscroll.set(str(0.0), str(self.to_normalized(widget_rows)))

    @staticmethod
    def _y_or_n(boolean):
        if boolean:
            return 'Y'
        else:
            return 'N'


class MachOInfo(object):
    """
    MachOInfo is a helper class that manages the information to be presented
    in SymbolWindow. There is one MachOInfo object per MachO in a binary.
    It contains a list of symbol tables and sections (for that MachO). It also
    holds the filtering results. The UI objects above only need to:

    1. Create a MachOInfo object for each mach_header header.
    2. Add a section object (to the MachOInfo object) for each section header.
    3. Add a symbol table object for each symtab_command header.
    4. Filter with the given symbol pattern.
    5. Get a symbol given an index from 0 to self.num_matched - 1.
    """
    def __init__(self, desc):
        self.desc = desc
        self._sections = list()
        # There should be only one symbol table per Mach-O but I cannot find documentation that
        # guarantee that constraint. So, if there are multiple LC_SYMTAB_COMMAND, we need to keep
        # a list of symbol tables.
        self._symbol_tables = list()
        self._filter_mappings = None
        self.num_matched = None

    def add_symbol_table(self, symbol_table):
        self._symbol_tables.append(symbol_table)

    def add_section(self, section):
        self._sections.append(section)

    def filter(self, pattern):
        self._filter_mappings = list()
        self.num_matched = 0
        for symbol_table in self._symbol_tables:
            indices = symbol_table.filter(pattern)
            self._filter_mappings.append(indices)
            self.num_matched += len(indices)
        return self.num_matched

    def num_symbols(self):
        return sum([len(st.symbols) for st in self._symbol_tables], 0)

    def symbol(self, matched_idx):
        assert 0 <= matched_idx < self.num_matched
        table_idx = 0
        section_desc = ''
        for mapping in self._filter_mappings:
            mapping_size = len(mapping)
            if matched_idx >= mapping_size:
                matched_idx -= mapping_size
                table_idx += 1
                continue
            (index, n_strx, n_type, n_sect, n_desc, n_value, symbol_name) = \
                self._symbol_tables[table_idx].symbols[mapping[matched_idx]]
            nlist = Nlist64(index=index,
                            n_strx=n_strx,
                            n_type=n_type,
                            n_sect=n_sect,
                            n_desc=n_desc,
                            n_value=n_value)
            if nlist.n_sect != 0:
                this_section = self._sections[nlist.n_sect]
                section_desc = '%s, %s' % \
                               (NullTerminatedStringField.get_string(this_section.segname),
                                NullTerminatedStringField.get_string(this_section.sectname))
            return nlist, symbol_name, section_desc
        assert False  # should never get here
