import Tkinter as Tk
import ttk
import tkFont
from ui.gui.auto_hide_scrollbar import AutoHideScrollbar


class TreeTable(ttk.Labelframe):
    """
    TreeTable is a generic hierarchical table widget. It provides a hierarchical left column keys
    and multiple columns of values. If used with only one level deep, it is just like a table.
    """
    FONT = None

    def __init__(self, parent, name, columns, **kwargs):
        if self.FONT is None:
            self.FONT = tkFont.Font(font='TkDefaultFont')
        self.columns = columns
        self.n_cols = len(self.columns)
        self.select_callback = None
        self.open_callback = None
        self.close_callback = None
        self._column_widths = [0] * len(columns)
        self._widget_width = None

        ttk.Labelframe.__init__(self, parent, text=name)

        self.tree = ttk.Treeview(self, columns=columns[1:], **kwargs)
        self.tree.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self._selected)
        self.tree.bind('<<TreeviewOpen>>', self._opened)
        self.tree.bind('<<TreeviewClose>>', self._closed)
        self.tree.bind('<Configure>', self._configured)

        self.yscroll = AutoHideScrollbar(self, orient=Tk.VERTICAL, command=self.tree.yview)
        self.yscroll.pack(side=Tk.RIGHT, fill=Tk.Y)

        self.tree.configure(yscrollcommand=self.yscroll.set)

        # Configure headings
        self.tree.heading('#0', text=columns[0])
        if self.n_cols > 1:
            for col in columns[1:]:
                self.tree.heading(col, text=col)

    def add(self, parent_id, row, values, **kwargs):
        assert len(values) == self.n_cols
        child_id = parent_id + '.' + str(row)
        self.tree.insert(parent=parent_id, index=row, iid=child_id, text=values[0], values=values[1:], **kwargs)
        for (idx, val) in enumerate(values):
            new_width = self.FONT.measure(val)
            if self._column_widths[idx] < new_width:
                self._column_widths[idx] = new_width
        return child_id

    def clear(self):
        for child in self.tree.get_children():
            self.tree.delete(child)
        self._column_widths = [0] * len(self._column_widths)

    def selected_path(self):
        selection = self.tree.selection()[0]
        return [int(x) for x in selection[1:].split('.')]

    def resize_columns(self):
        total = sum(self._column_widths)
        if total == 0:
            return
        print 'COL_WIDTHS:', self._column_widths
        RIGHT_GAP = 3
        widget_width = self._widget_width
        if self._widget_width > RIGHT_GAP:
            widget_width -= RIGHT_GAP  # leave a little gap on the right
        scale = float(widget_width) / float(total)
        self.tree.column('#0', width=int(self._column_widths[0] * scale))
        for idx in xrange(1, len(self.columns)):
            self.tree.column(self.columns[idx], width=int(self._column_widths[idx] * scale))

    def _selected(self, event):
        assert event is not None  # use 'event' to get rid of a PyCharm warning.
        if callable(self.select_callback):
            self.select_callback(self.selected_path())

    def _opened(self, event):
        assert event is not None
        if callable(self.open_callback):
            self.open_callback(self.selected_path())

    def _closed(self, event):
        assert event is not None
        if callable(self.close_callback):
            self.close_callback(self.selected_path())

    def _configured(self, event):
        self._widget_width = event.width
        print 'TREE VIEW CONFIGURED[%s]:' % self.__class__, event.width, event.height
        self.update_idletasks()
        self.resize_columns()
