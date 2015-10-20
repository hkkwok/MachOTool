import ttk as ttk


class AutoHideScrollbar(ttk.Scrollbar):
    def __init__(self, parent, **kwargs):
        ttk.Scrollbar.__init__(self, parent, **kwargs)
        self.width = self._get_width()

    def _get_width(self):
        return float(self.cget('width'))

    def _set_width(self, enabled):
        if enabled:
            self.configure(width=self.width)
        else:
            self.configure(width=0)

    def set(self, first, last):
        cur_width = self._get_width()
        if float(first) == 0 and float(last) == 1:
            if cur_width > 0:
                self._set_width(False)
        else:
            if cur_width == 0:
                self._set_width(True)
        ttk.Scrollbar.set(self, first, last)
