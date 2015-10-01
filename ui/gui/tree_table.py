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
from ui.gui.auto_hide_scrollbar import AutoHideScrollbar


class TreeTable(ttk.Labelframe):
    """
    TreeTable is a generic hierarchical table widget. It provides a hierarchical left column keys
    and multiple columns of values. If used with only one level deep, it is just like a table.
    """
    def __init__(self, parent, name, columns, **kwargs):
        self.columns = columns
        self.n_cols = len(self.columns)
        self.callback = None

        ttk.Labelframe.__init__(self, parent, text=name)

        self.tree = ttk.Treeview(self, columns=columns[1:], **kwargs)
        self.tree.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.selected)

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
        return child_id

    def clear(self):
        for child in self.tree.get_children():
            self.tree.delete(child)

    def selected_path(self):
        selection = self.tree.selection()[0]
        return [int(x) for x in selection[1:].split('.')]

    def selected(self, event):
        assert event is not None  # use 'event' to get rid of a PyCharm warning.
        if callable(self.callback):
            self.callback(self.selected_path())
