try:
    # Python 2
    import Tkinter as Tk
    import tkFont as tkFont
    import ttk
except ImportError:
    # Python 3
    import tkinter as Tk
    import tkinter.ttk as ttk
    import tkinter.font as tkFont
import string

from utils.header import Header
from tree_table import TreeTable
from window_tab import WindowTab
from auto_hide_scrollbar import AutoHideScrollbar


class DecodeWindow(WindowTab):
    TITLE = 'Decode'

    def __init__(self, parent):
        WindowTab.__init__(self, parent)

        # Create the 3 panels
        self.outer_panedwindow = ttk.Panedwindow(self, orient=Tk.VERTICAL)
        self.outer_panedwindow.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)
        self.inner_panedwindow = ttk.Panedwindow(self.outer_panedwindow, orient=Tk.HORIZONTAL)
        self.outer_panedwindow.add(self.inner_panedwindow)

        # A bytes range tree on the left
        self.bytes_range_tree = BytesRangeTree(self.inner_panedwindow)
        self.bytes_range_tree.callback = self.header_selected
        self.bytes_range_tree.configure(width=200, height=100, padding=5)
        self.inner_panedwindow.add(self.bytes_range_tree)

        # A table of header key-value pairs on the right
        self.header_table = FieldValueTable(self.inner_panedwindow)
        self.header_table.callback = self.field_selected
        self.header_table.configure(width=100, height=100, padding=5)
        self.inner_panedwindow.add(self.header_table)

        # A byte table at the bottom
        self.bytes_table = BytesTable(self.outer_panedwindow)
        self.bytes_table.configure(width=300, height=100, padding=5)
        self.outer_panedwindow.add(self.bytes_table)

    def clear(self):
        self.bytes_range = None
        self.bytes_range_tree.clear()
        self.header_table.clear()
        self.bytes_table.clear()

    def load(self, bytes_range, bytes_):
        self.clear()
        self.bytes_range = bytes_range
        if self.bytes_range is not None:
            self._add_subtree('', self.bytes_range)
        if bytes_ is not None:
            self.bytes_table.add_bytes(bytes_.bytes)

    def _add_subtree(self, parent_id, br):
        for idx in range(len(br.subranges)):
            subrange = br.subranges[idx]
            if hasattr(subrange.data, 'name'):
                desc = subrange.data.name
            else:
                desc = str(subrange.data)
            (start, stop) = subrange.abs_range()
            child_id = self.bytes_range_tree.add(parent_id, idx, values=(desc, format(start, ','), format(stop, ',')))
            self._add_subtree(child_id, subrange)

    def _bytes_range_from_path(self, path):
        br = self.bytes_range
        while len(path) > 0:
            next_idx = path.pop(0)
            br = br.subranges[next_idx]
        return br

    def header_selected(self, path):
        assert len(path) > 0
        br = self._bytes_range_from_path(path)
        start, stop = br.abs_range()
        if isinstance(br.data, Header):
            self.header_table.set_header(br.data)
        self.bytes_table.mark_bytes(start, stop)

    def field_selected(self, path):
        assert len(path) == 1
        header = self.header_table.header
        assert header is not None
        offset, size = header.get_offset_size(path[0])
        if offset is None:
            return
        br = self._bytes_range_from_path(self.bytes_range_tree.selected_path())
        start = br.abs_start()
        self.bytes_table.mark_bytes(start + offset, start + offset + size)


class BytesRangeTree(TreeTable):
    def __init__(self, parent, **kwargs):
        TreeTable.__init__(self, parent, 'Bytes Ranges', ('Header', 'Start', 'Stop'), **kwargs)
        self.tree.column('Start', width=80, stretch=False, anchor=Tk.E)
        self.tree.column('Stop', width=80, stretch=False, anchor=Tk.E)
        self.tree.configure(selectmode='browse')
        self.callback = None


class FieldValueTable(TreeTable):
    LIGHT_BLUE_TAG_NAME = 'light_blue_background'

    def __init__(self, parent, **kwargs):
        self.header = None
        TreeTable.__init__(self, parent, name='Header', columns=('Field', 'Value'), **kwargs)
        self.tree.tag_configure(self.LIGHT_BLUE_TAG_NAME, background='#e0e8f0')

    def add(self, parent_id, row, values, **kwargs):
        if row % 2 == 1:
            kwargs['tag'] = self.LIGHT_BLUE_TAG_NAME
        TreeTable.add(self, parent_id, row, values, **kwargs)

    def set_header(self, header):
        assert isinstance(header, Header)
        self.header = header

        self.clear()
        idx = 0
        for field in header.FIELDS:
            self.add('', idx, values=(field.name, field.display(header)))
            idx += 1


class BytesTable(ttk.Labelframe):
    BYTES_PER_ROW = 16
    FONT_FAMILY = 'Courier New'
    FONT = None
    COLUMNS = ('Offset', '0', '1', '2', '3', '4', '5', '6', '7',
               '8', '9', '10', '11', '12', '13', '14', '15', 'Characters')
    FONT_TAG_NAME = 'fixed_width_font'
    MARK_TAG_NAME = 'highlight_background'

    def __init__(self, parent):
        ttk.Labelframe.__init__(self, parent, text='Bytes')
        self.text = Tk.Text(self)
        self.text.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        if self.FONT is None:
            self.FONT = tkFont.Font(family=self.FONT_FAMILY, size=14, weight='normal')
            self.text.tag_configure(self.FONT_TAG_NAME, font=self.FONT)
            self.text.tag_configure(self.MARK_TAG_NAME, background='#d0f0d8')

        self.yscroll = AutoHideScrollbar(self, orient=Tk.VERTICAL, command=self.text.yview)
        self.yscroll.pack(side=Tk.RIGHT, fill=Tk.Y)

        self.text.configure(yscrollcommand=self.yscroll.set)
        self.end_offset = None
        self.mark_ranges = None
        self.rows = None
        self.clear()

    def clear(self):
        self.end_offset = None
        self.rows = 1
        self.mark_ranges = list()
        self.text.configure(state=Tk.NORMAL)
        self.text.delete('1.0', 'end')
        self.text.configure(state=Tk.DISABLED)

    @staticmethod
    def _printable_char(ch):
        if ch in string.punctuation or ch in string.ascii_letters:
            return ch
        return '.'

    @classmethod
    def _printable(cls, s):
        return ''.join(cls._printable_char(x) for x in s)

    def _add_one_row(self, row, bytes_, start_offset):
        assert start_offset % self.BYTES_PER_ROW == 0
        assert len(bytes_) <= self.BYTES_PER_ROW
        start_addr = '%016x' % start_offset
        hexes = ['%02x' % ord(x) for x in bytes_]
        if len(hexes) != self.BYTES_PER_ROW:
            hexes += ['  '] * (self.BYTES_PER_ROW - len(hexes))
        chars = self._printable(bytes_)
        line = start_addr + '    ' + ' '.join(hexes) + '    ' + chars + '\n'
        self.text.insert('%d.0' % row, line, self.FONT_TAG_NAME)

    def add_bytes(self, bytes_, base_offset=0):
        self.text.configure(state=Tk.NORMAL)
        self.end_offset = len(bytes_)
        self.rows = 1
        for offset in range(0, self.end_offset, self.BYTES_PER_ROW):
            start = base_offset + offset
            stop = base_offset + min(self.end_offset, start + self.BYTES_PER_ROW)
            self._add_one_row(self.rows, bytes_[start:stop], start)
            self.rows += 1
        self.text.configure(state=Tk.DISABLED)

    def _mark_one_row(self, row, start, stop):
        def start_byte_column(offset):
            return 16 + 4 + 3 * offset

        def stop_byte_column(offset):
            return start_byte_column(offset) - 1

        def char_column(offset):
            return 71 + offset

        def column2index(r, c):
            return '%d.%d' % (1 + r, c)

        start_col = start_byte_column(start)
        stop_col = stop_byte_column(stop)
        start_index = column2index(row, start_col)
        stop_index = column2index(row, stop_col)
        self.text.tag_add(self.MARK_TAG_NAME, start_index, stop_index)
        self.mark_ranges.append((start_index, stop_index))

        start_col = char_column(start)
        stop_col = char_column(stop)
        start_index = column2index(row, start_col)
        stop_index = column2index(row, stop_col)
        self.text.tag_add(self.MARK_TAG_NAME, start_index, stop_index)
        self.mark_ranges.append((start_index, stop_index))

    def mark_bytes(self, start, stop):
        self.text.configure(state=Tk.NORMAL)
        if len(self.mark_ranges) > 0:
            for (start_index, stop_index) in self.mark_ranges:
                self.text.tag_remove(self.MARK_TAG_NAME, start_index, stop_index)
            self.mark_ranges = list()

        start_row, start_col = divmod(start, self.BYTES_PER_ROW)
        stop_row, stop_col = divmod(stop, self.BYTES_PER_ROW)
        self.scroll_to(start_row, stop_row)

        if start_row == stop_row:
            # Special case - just one row
            self._mark_one_row(start_row, start_col, stop_col)
        else:
            if start_col != 0:
                # Process prologue
                self._mark_one_row(start_row, start_col, self.BYTES_PER_ROW)
                start = (start_row + 1) * self.BYTES_PER_ROW
            if stop_col != 0:
                # Process epilogue
                self._mark_one_row(stop_row, 0, stop_col)
                stop -= stop_col
            if start == stop:
                pass  # special case two incomplete rows
            else:
                assert start % self.BYTES_PER_ROW == 0 and stop % self.BYTES_PER_ROW == 0
                for row in range(start_row, stop_row):
                    self._mark_one_row(row, 0, self.BYTES_PER_ROW)
        self.text.configure(state=Tk.DISABLED)

    def scroll_to(self, start_row, stop_row):
        """
        Scroll a range of lines from start_row to stop_row (both inclusive). It tries to center
        the line range. However, if the line range is larger than text view, it keeps 10% (of the
        text view) gap on the top so that one can clearly see the beginning of the selected lines.
        """
        (view_top, view_bottom) = self.yscroll.get()
        mark_top = float(start_row) / float(self.rows)
        mark_bottom = float(stop_row) / float(self.rows)

        view_size = view_bottom - view_top
        mark_size = mark_bottom - mark_top

        gap = max(0.2 * view_size, view_size - mark_size)
        self.text.yview('moveto', max(0.0, mark_top - 0.5 * gap))
