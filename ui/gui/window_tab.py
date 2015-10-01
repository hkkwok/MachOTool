try:
    import ttk as ttk
except ImportError:
    import tkinter.ttk as ttk


class WindowTab(ttk.Frame):
    TITLE = None  # derived class must redefine this

    def __init__(self, parent):
        assert self.TITLE is not None
        ttk.Frame.__init__(self, parent)
        self.bytes_range = None
        self.bytes = None

    def is_loaded(self):
        return self.bytes_range is not None

    def clear(self):
        raise NotImplementedError()

    def load(self, bytes_range, bytes_):
        raise NotImplementedError()

    def widget_id(self):
        return self.winfo_parent() + '.' + self.winfo_name()