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
from utils.progress_indicator import ProgressIndicator
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
        self.bytes_range_tree.select_callback = self.header_selected
        self.bytes_range_tree.open_callback = self.block_opened
        self.bytes_range_tree.configure(width=200, height=100, padding=5)
        self.inner_panedwindow.add(self.bytes_range_tree)

        # A table of header key-value pairs on the right
        self.header_table = FieldValueTable(self.inner_panedwindow)
        self.header_table.select_callback = self.field_selected
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
        def get_values(sr):
            if hasattr(sr.data, 'name'):
                desc = sr.data.name
            else:
                desc = str(sr.data)
            (start, stop) = sr.abs_range()
            return desc, format(start, ','), format(stop, ',')

        pi = ProgressIndicator('show bytes ranges...', 1)
        for idx in xrange(len(br.subranges)):
            subrange = br.subranges[idx]
            child_id = parent_id + '.%d' % idx
            if not self.bytes_range_tree.tree.exists(child_id):
                child_id = self.bytes_range_tree.add(parent_id, idx, values=get_values(subrange))
            if len(subrange.subranges) > 0:
                # if there are subsubranges, just insert 1st row so that the open icon is shown
                if not self.bytes_range_tree.tree.exists(child_id + '.0'):
                    subsubrange = subrange.subranges[0]
                    self.bytes_range_tree.add(child_id, 0, values=get_values(subsubrange))
            pi.click()
        pi.done()

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

    def block_opened(self, path):
        br = self.bytes_range
        parent_id = ''
        for idx in path:
            br = br.subranges[idx]
            parent_id += '.' + str(idx)
        self._add_subtree(parent_id, br)


class BytesRangeTree(TreeTable):
    def __init__(self, parent, **kwargs):
        TreeTable.__init__(self, parent, 'Bytes Ranges', ('Header', 'Start', 'Stop'), **kwargs)
        self.tree.column('Start', width=80, stretch=False, anchor=Tk.E)
        self.tree.column('Stop', width=80, stretch=False, anchor=Tk.E)
        self.tree.configure(selectmode='browse')
        self.select_callback = None


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
        self.text = Tk.Text(self, wrap=Tk.NONE)
        self.text.bind('<MouseWheel>', self._text_scrolled)
        self.text.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        if self.FONT is None:
            self.FONT = tkFont.Font(family=self.FONT_FAMILY, size=14, weight='normal')
            self.text.tag_configure(self.FONT_TAG_NAME, font=self.FONT)
            self.text.tag_configure(self.MARK_TAG_NAME, background='#d0f0d8')

        self.yscroll = AutoHideScrollbar(self, orient=Tk.VERTICAL, command=self.yview)
        self.yscroll.pack(side=Tk.RIGHT, fill=Tk.Y)

        self.text.configure()
        self.end_offset = None
        self.mark_ranges = None
        self.rows = None
        self.bytes = None
        self.base_offset = None
        self.widget_start = None  # starting visible row
        self.widget_stop = None   # stopping (inclusive) visible row
        self.marked_bytes = MarkedBytes()
        self.clear()

    def clear(self):
        self.clear_states()
        self.clear_ui()

    def clear_ui(self):
        self.text.configure(state=Tk.NORMAL)
        self.text.delete('1.0', 'end')
        self.text.configure(state=Tk.DISABLED)
        self.widget_start = None
        self.widget_stop = None
        self.marked_bytes.reset()

    def clear_states(self):
        self.end_offset = None
        self.rows = 1
        self.mark_ranges = list()
        self.base_offset = None

    def widget_rows(self):
        # TODO - This is not being updated but the initial value is good enough for now
        return int(self.text.cget('height'))

    def _update_begin(self):
        self.text.configure(state=Tk.NORMAL)

    def _update_end(self):
        self.text.configure(state=Tk.DISABLED)

    def _text_scrolled(self, event):
        adjustment = event.delta
        if adjustment > 0:
            adjustment = 1
        elif adjustment < 0:
            adjustment = -1
        self.yview('scroll', adjustment, 'units')

    def yview(self, *args):
        self._yview(False, *args)

    def _yview(self, forced_update, *args):
        #print 'YVIEW', args
        action = args[0]
        if action == 'moveto':
            start_row = self._normalized_to_row(args[1])
            stop_row = start_row + self.widget_rows()
        elif action == 'scroll':
            amount = int(args[1])
            unit = args[2]
            if unit == 'page':
                adjustment = self.widget_rows() - 1
            elif unit == 'units':
                adjustment = 1
            else:
                print 'Unknown unit %s' % unit
                return
            adjustment *= amount
            start_row = self.widget_start + adjustment
            stop_row = self.widget_stop + adjustment
        else:
            print 'Unknown action %s' % action
            return
        # Check we scroll past the end. Move it up
        delta = stop_row - self.rows - 1
        if delta > 0:
            start_row -= delta
            stop_row -= delta
        # Check we scroll past the beginning. Move it down
        delta = 0 - start_row
        if delta > 0:
            start_row += delta
            stop_row += delta

        if not forced_update and start_row == self.widget_start and stop_row == self.widget_stop:
            return

        assert self.widget_start <= self.widget_stop
        assert start_row <= stop_row

        self._show(start_row, stop_row)
        self.yscroll.set(str(self._row_to_normalized(start_row)),
                         str(self._row_to_normalized(stop_row)))

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

    def _normalized_to_row(self, normalized):
        return int(float(normalized) * self.rows)

    def _normalized_to_row_roundup(self, normalized):
        return int(float(normalized) * self.rows + 0.5)

    def _row_to_normalized(self, row):
        return float(row) / self.rows

    def _validate_rows(self, start, stop):
        assert self.widget_start <= start <= self.widget_stop
        assert self.widget_start <= stop <= self.widget_stop

    def add_bytes(self, bytes_, base_offset=0):
        self.base_offset = base_offset
        self.bytes = bytes_
        self.end_offset = len(bytes_)
        self.rows = self._offset_to_row_roundup(self.end_offset)
        self._show(0, self.widget_rows())

    def _show_rows(self, start, stop):
        self._validate_rows(start, stop)
        for row in xrange(start, stop + 1):
            line = self._format_row(row)
            real_row = row - self.widget_start + 1
            self.text.insert('%d.0' % real_row, line)
            start_col, stop_col = self.marked_bytes.marked_range(row)
            if start_col is not None:
                self._mark_one_row(row, start_col, stop_col)

    def _hide_rows(self, start, stop):
        self._validate_rows(start, stop)
        real_start = start - self.widget_start + 1
        real_stop = stop - self.widget_start + 1
        self.text.delete('%d.0' % real_start, '%d.88' % real_stop)

    def _update_widget_rows(self, start, stop):
        self.widget_start = start
        self.widget_stop = stop

    def _show(self, start_row, stop_row):
        #print 'SHOW: (%s, %s) -> (%s, %s)' % \
        #      (str(self.widget_start), str(self.widget_stop), str(start_row), str(stop_row))
        self._update_begin()
        self.text.delete('1.0', 'end')
        self._update_widget_rows(start_row, stop_row)
        self._show_rows(start_row, stop_row)
        self.update_idletasks()
        self._update_end()

    def _mark_one_row(self, row, start, stop):
        def start_byte_column(offset):
            return 16 + 4 + 3 * offset

        def stop_byte_column(offset):
            return start_byte_column(offset) - 1

        def char_column(offset):
            return 71 + offset

        def column2index(r, c):
            return '%d.%d' % (1 + r - self.widget_start, c)

        if row < self.widget_start or row > self.widget_stop:
            return False
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
        mark_top = self._row_to_normalized(start_row)
        mark_bottom = self._row_to_normalized(stop_row)

        view_size = self._row_to_normalized(self.widget_rows())
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
        self.start_row, self.start_col = divmod(start, BytesTable.BYTES_PER_ROW)
        self.stop_row, self.stop_col = divmod(stop, BytesTable.BYTES_PER_ROW)

    def is_marked(self, row):
        return self.start_row <= row <= self.stop_row

    def marked_range(self, row):
        if not self.is_marked(row):
            return None, None
        start_col = 0
        stop_col = BytesTable.BYTES_PER_ROW
        if self.start_row == row:
            start_col = self.start_col
        if self.stop_row == row:
            stop_col = self.stop_col
        return start_col, stop_col