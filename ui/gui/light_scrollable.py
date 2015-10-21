import Tkinter as Tk
import ttk
from auto_hide_scrollbar import AutoHideScrollbar


class LightScrollableWidget(ttk.Labelframe):
    """
    LightScrollableWidget is an abstract base class for creating scrollable, line-oriented widgets
    that have low memory consumption. The problem arises when I found that there are 2.6 millions
    symbols in a real app that I used for testing.

    The problem is that conventional Tkinter Text+ScrollBar / Treeview widget does not work because
    it would require adding millions of rows. The memory consumption is enormous and the run-time
    (for adding so many rows) feels like eternity.

    The solution is to use the scrolled widget to display only what is visible and manage the
    scrollbar (and other scrolling event) ourselves. This way we only need to draw / store all
    hand full of rows.

    Each LightScrollableWidget must contain a widget. This widget needs
    """
    CONFIG_HEIGHT = 'height'
    CONFIG_WIDTH = 'width'

    def __init__(self, parent, title, widget_fn):
        ttk.Labelframe.__init__(self, parent, text=title)
        self.widget = widget_fn(self)
        self.widget.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=True)
        self.widget.bind('<MouseWheel>', self._scrolled)
        self.widget.bind('<Configure>', self._configured)

        self.yscroll = AutoHideScrollbar(self, orient=Tk.VERTICAL, command=self.yview)
        self.yscroll.pack(side=Tk.RIGHT, fill=Tk.Y, expand=False)

        self._widget_start = None
        self._widget_stop = None
        self._widget_height = None  # the height of the widget in units of pixel
        self._widget_width = None  # the width of the widget in units of pixel
        self.rows = 0  # Number of rows
        self.index_base = 0

        # This callback is made in a <Configure> event, the parameter is a list of string listed
        # above (CONFIG_XXX). Each string indicates what attributes are configured.
        self.configured_callback = None

    def set_rows(self, rows):
        self.rows = rows

    def clear_widget(self):
        """
        Must be overridden by derived class. Clear all content in the base widget.
        """
        raise NotImplementedError()

    def widget_rows(self):
        """
        Must be overridden by derived class.
        :return: Return the number of rows of the base widget
        """
        raise NotImplementedError()

    def row_height(self):
        """
        Must be overridden by derived class.
        :return: Return the height of one row in units of pixel.
        """
        raise NotImplementedError()

    def update_begin(self):
        """
        If the base widget is normally in a DISABLED state, enable the base widget for update.
        :return: None
        """
        pass

    def update_end(self):
        """
        If the base widget is normally in a DISABLE state, disable the base widget for update.
        :return: None
        """
        pass

    def show_row(self, data_row, view_row):
        """
        Must be overridden by derived class. Add a row of data into the base widget
        :param data_row: The row number of data row indexing system.
        :param view_row: The row number in view row indexing system.
        :return: None
        """
        raise NotImplementedError()

    def is_visible(self, data_row):
        return self._widget_start <= data_row <= self._widget_stop

    # Some notes on the indexing systems. Tk uses a normalized indexing system
    # ranging from [0, 1]. The unnormalized indexing system is the data row
    # index ranging from [0, self.rows - 1]

    def to_view_row(self, data_row):
        assert 0 <= data_row < self.rows
        return data_row - self._widget_start + self.index_base

    def to_normalized(self, row):
        assert 0 <= row < self.rows
        return float(row) / float(self.rows - 1)

    def to_unnormalized(self, normalized, round_up=False):
        normalized_flaot = float(normalized)
        assert 0.0 <= normalized_flaot <= 1.0
        row = normalized_flaot * (self.rows - 1)
        if round_up:
            row += 0.5
        return int(row)

    def _scrolled(self, event):
        adjustment = event.delta
        if adjustment > 0 and self._widget_start == 0:
            return
        if adjustment < 0 and self._widget_stop == (self.rows - 1):
            return
        self.yview('scroll', str(adjustment), 'units')

    def _configured(self, event):
        cfg_list = list()
        if event.height != self._widget_height:
            self._widget_height = event.height
            self.yview('moveto', self.yscroll.get()[0])
            cfg_list.append(self.CONFIG_HEIGHT)
        if event.width != self._widget_width:
            self._widget_width = event.width
            cfg_list.append(self.CONFIG_WIDTH)
        if callable(self.configured_callback):
            self.configured_callback(cfg_list)

    def yview(self, *args):
        self._yview(False, *args)

    def _yview(self, forced_update, *args):
        if self.rows == 0:
            return
        action = args[0]
        if action == 'moveto':
            start_row = self.to_unnormalized(args[1])
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
            adjustment *= -amount
            start_row = self._widget_start + adjustment
            stop_row = self._widget_stop + adjustment
        else:
            print 'Unknown action %s' % action
            return
        # Check we scroll past the end. Move it up
        delta = stop_row - (self.rows - 1)
        if delta > 0:
            start_row -= delta
            stop_row -= delta
        # Check we scroll past the beginning. Move it down
        delta = 0 - start_row
        if delta > 0:
            start_row += delta
            stop_row += delta
        # Clip the stop row to no more than the total # of data row
        if stop_row >= self.rows:
            stop_row = self.rows - 1

        if not forced_update and start_row == self._widget_start and stop_row == self._widget_stop:
            return

        assert self._widget_start <= self._widget_stop
        assert start_row <= stop_row

        self._show(start_row, stop_row)
        self.yscroll.set(str(self.to_normalized(start_row)),
                         str(self.to_normalized(stop_row)))

    def _validate_rows(self, start, stop):
        assert self._widget_start <= start <= self._widget_stop
        assert self._widget_start <= stop <= self._widget_stop

    def _update_widget_rows(self, start_row, stop_row):
        self._widget_start = start_row
        self._widget_stop = stop_row

    def _show(self, start_row, stop_row):
        self.update_begin()
        self.clear_widget()
        self._update_widget_rows(start_row, stop_row)
        self._show_rows(start_row, stop_row)
        self.widget.yview('moveto', '0.0')
        self.update_idletasks()
        self.update_end()

    def _show_rows(self, start, stop):
        self._validate_rows(start, stop)
        for row in xrange(start, stop + 1):
            self.show_row(row, row - self._widget_start + self.index_base)
