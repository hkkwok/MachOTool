import Tkinter as Tk
import tkFont as tkFont
import ttk
import string

from utils.header import Header
from utils.progress_indicator import ProgressIndicator
from tree_table import TreeTable
from window_tab import WindowTab
from light_scrollable import LightScrollableWidget


class DecodeWindow(WindowTab):
    TITLE = 'Decode'

    def __init__(self, parent):
        WindowTab.__init__(self, parent)

        # Create the 3 views
        self.outer_panedwindow = ttk.Panedwindow(self, orient=Tk.VERTICAL)
        self.outer_panedwindow.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)
        self.inner_panedwindow = ttk.Panedwindow(self.outer_panedwindow, orient=Tk.HORIZONTAL)
        self.outer_panedwindow.add(self.inner_panedwindow)

        # A byte range tree on the left
        self.byte_range_tree = ByteRangeView(self.inner_panedwindow)
        self.byte_range_tree.select_callback = self.header_selected
        self.byte_range_tree.open_callback = self.block_opened
        self.byte_range_tree.configure(width=200, height=100, padding=5)
        self.inner_panedwindow.add(self.byte_range_tree)

        # A table of header key-value pairs on the right
        self.header_table = FieldValueView(self.inner_panedwindow)
        self.header_table.select_callback = self.field_selected
        self.header_table.configure(width=100, height=100, padding=5)
        self.inner_panedwindow.add(self.header_table)

        # A byte table at the bottom
        self.bytes_table = BytesView(self.outer_panedwindow)
        self.bytes_table.configure(width=300, height=100, padding=5)
        self.outer_panedwindow.add(self.bytes_table)

    def clear(self):
        self.byte_range = None
        self.byte_range_tree.clear()
        self.header_table.clear()
        self.bytes_table.clear()

    def load(self, byte_range, bytes_):
        self.clear()
        self.byte_range = byte_range
        if self.byte_range is not None:
            self._add_subtree('', self.byte_range)
        if bytes_ is not None:
            self.bytes_table.add_bytes(bytes_.bytes)

    def _add_subtree(self, parent_id, br):
        def get_values(sr):
            if hasattr(sr.data, 'name'):
                desc = sr.data.name
            else:
                desc = str(sr.data)
            (start, stop) = sr.abs_range()
            return desc, format(start, ','), format(stop, ',')

        pi = ProgressIndicator('show byte ranges...', 1)
        for idx in xrange(len(br.subranges)):
            subrange = br.subranges[idx]
            child_id = parent_id + '.%d' % idx
            if not self.byte_range_tree.tree.exists(child_id):
                child_id = self.byte_range_tree.add(parent_id, idx, values=get_values(subrange))
            if len(subrange.subranges) > 0:
                # if there are subsubranges, just insert 1st row so that the open icon is shown
                if not self.byte_range_tree.tree.exists(child_id + '.0'):
                    subsubrange = subrange.subranges[0]
                    self.byte_range_tree.add(child_id, 0, values=get_values(subsubrange))
            pi.click()
        pi.done()

    def _byte_range_from_path(self, path):
        br = self.byte_range
        while len(path) > 0:
            next_idx = path.pop(0)
            br = br.subranges[next_idx]
        return br

    def header_selected(self, path):
        assert len(path) > 0
        br = self._byte_range_from_path(path)
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
        br = self._byte_range_from_path(self.byte_range_tree.selected_path())
        start = br.abs_start()
        self.bytes_table.mark_bytes(start + offset, start + offset + size)

    def block_opened(self, path):
        br = self.byte_range
        parent_id = ''
        for idx in path:
            br = br.subranges[idx]
            parent_id += '.' + str(idx)
        self._add_subtree(parent_id, br)


class ByteRangeView(TreeTable):
    def __init__(self, parent, **kwargs):
        TreeTable.__init__(self, parent, 'Byte Ranges', ('Header', 'Start', 'Stop'), **kwargs)
        self.tree.column('Start', width=80, stretch=False, anchor=Tk.E)
        self.tree.column('Stop', width=80, stretch=False, anchor=Tk.E)
        self.tree.configure(selectmode='browse')
        self.select_callback = None


class FieldValueView(TreeTable):
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


class BytesView(LightScrollableWidget):
    BYTES_PER_ROW = 16
    FONT_FAMILY = 'Courier New'
    FONT = None
    COLUMNS = ('Offset', '0', '1', '2', '3', '4', '5', '6', '7',
               '8', '9', '10', '11', '12', '13', '14', '15', 'Characters')
    FONT_TAG_NAME = 'fixed_width_font'
    MARK_TAG_NAME = 'highlight_background'

    def __init__(self, parent):
        LightScrollableWidget.__init__(self, parent, 'Bytes', lambda p: Tk.Text(p, wrap=Tk.NONE))
        if self.FONT is None:
            self.FONT = tkFont.Font(family=self.FONT_FAMILY, size=14, weight='normal')
            self.widget.tag_configure(self.FONT_TAG_NAME, font=self.FONT)
            self.widget.tag_configure(self.MARK_TAG_NAME, background='#d0f0d8')

        self.index_base = 1
        self.bytes = None
        self.base_offset = None
        self.end_offset = None
        self.mark_ranges = None
        self.marked_bytes = MarkedBytes()
        self.clear()

    def clear(self):
        self.clear_states()
        self.clear_ui()

    def clear_ui(self):
        self.widget.configure(state=Tk.NORMAL)
        self.widget.delete('1.0', 'end')
        self.widget.configure(state=Tk.DISABLED)
        self.marked_bytes.reset()

    def clear_states(self):
        self.base_offset = None
        self.end_offset = None
        self.set_rows(1)
        self.mark_ranges = list()

    def widget_rows(self):
        if self._widget_height is None:
            return int(self.widget.cget('height'))
        return self._widget_height / self.row_height()

    def update_begin(self):
        self.widget.configure(state=Tk.NORMAL)

    def update_end(self):
        self.widget.configure(state=Tk.DISABLED)

    def clear_widget(self):
        self.widget.delete('1.0', 'end')
        self._update_widget_rows(None, None)

    def row_height(self):
        font_height = self.FONT.metrics('linespace')
        return font_height

    @staticmethod
    def _printable_char(ch):
        if ch in string.punctuation or ch in string.ascii_letters:
            return ch
        return '.'

    @classmethod
    def _printable(cls, s):
        out = ''
        for ch in s:
            out += cls._printable_char(ch)
        return out

    def _format_row(self, row):
        offset = row * self.BYTES_PER_ROW
        start = self.base_offset + offset
        stop = self.base_offset + min(self.end_offset, start + self.BYTES_PER_ROW)
        bytes_ = self.bytes[start:stop]

        start_addr = '%016x' % start
        hexes = ['%02x' % ord(x) for x in bytes_]
        if len(hexes) != self.BYTES_PER_ROW:
            hexes += ['  '] * (self.BYTES_PER_ROW - len(hexes))
        chars = self._printable(bytes_)
        if len(chars) != self.BYTES_PER_ROW:
            chars += ' ' * (self.BYTES_PER_ROW - len(chars))
        line = start_addr + '    ' + ' '.join(hexes) + '    ' + chars + '\n'
        assert len(line) == 88
        return line

    def _offset_to_row(self, offset):
        return offset / self.BYTES_PER_ROW

    def _offset_to_row_roundup(self, offset):
        return (offset + self.BYTES_PER_ROW - 1) / self.BYTES_PER_ROW

    def add_bytes(self, bytes_, base_offset=0):
        self.base_offset = base_offset
        self.bytes = bytes_
        self.end_offset = len(bytes_)
        self.set_rows(self._offset_to_row_roundup(self.end_offset))
        self._show(0, self.widget_rows())

    def show_row(self, data_row, view_row):
        line = self._format_row(data_row)
        self.widget.insert('%d.0' % view_row, line)
        start_col, stop_col = self.marked_bytes.marked_range(data_row)
        if start_col is not None:
            self._mark_one_row(data_row, start_col, stop_col)

    def _mark_one_row(self, row, start, stop):
        def start_byte_column(offset):
            return 16 + 4 + 3 * offset

        def stop_byte_column(offset):
            return start_byte_column(offset) - 1

        def char_column(offset):
            return 71 + offset

        def column2index(r, c):
            return '%d.%d' % (self.to_view_row(r), c)

        if not self.is_visible(row):
            return False
        start_col = start_byte_column(start)
        stop_col = stop_byte_column(stop)
        start_index = column2index(row, start_col)
        stop_index = column2index(row, stop_col)
        self.widget.tag_add(self.MARK_TAG_NAME, start_index, stop_index)
        self.mark_ranges.append((start_index, stop_index))

        start_col = char_column(start)
        stop_col = char_column(stop)
        start_index = column2index(row, start_col)
        stop_index = column2index(row, stop_col)
        self.widget.tag_add(self.MARK_TAG_NAME, start_index, stop_index)
        self.mark_ranges.append((start_index, stop_index))
        return True

    def mark_bytes(self, start, stop):
        self.marked_bytes.set(start, stop)
        self._scroll_to(self.marked_bytes.start_row, self.marked_bytes.stop_row)

    def _scroll_to(self, start_row, stop_row):
        """
        Scroll a range of lines from start_row to stop_row (both inclusive). It tries to center
        the line range. However, if the line range is larger than text view, it keeps 10% (of the
        text view) gap on the top so that one can clearly see the beginning of the selected lines.
        """
        mark_top = self.to_normalized(start_row)
        mark_bottom = self.to_normalized(stop_row)

        view_size = self.to_normalized(self.widget_rows())
        mark_size = mark_bottom - mark_top

        gap = max(0.2 * view_size, view_size - mark_size)
        self._yview(True, 'moveto', str(max(0.0, mark_top - 0.5 * gap)))


class MarkedBytes(object):
    def __init__(self):
        self.start_row = None
        self.start_col = None
        self.stop_row = None
        self.stop_col = None

    def reset(self):
        self.start_row = None
        self.start_col = None
        self.stop_row = None
        self.stop_col = None

    def set(self, start, stop):
        self.start_row, self.start_col = divmod(start, BytesView.BYTES_PER_ROW)
        self.stop_row, self.stop_col = divmod(stop + BytesView.BYTES_PER_ROW - 1, BytesView.BYTES_PER_ROW)
        self.stop_row -= 1

    def is_marked(self, row):
        return self.start_row <= row <= self.stop_row

    def marked_range(self, row):
        if not self.is_marked(row):
            return None, None
        start_col = 0
        stop_col = BytesView.BYTES_PER_ROW
        if self.start_row == row:
            start_col = self.start_col
        if self.stop_row == row:
            stop_col = self.stop_col
        return start_col, stop_col