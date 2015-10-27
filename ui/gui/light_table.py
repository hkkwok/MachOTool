import ttk
import tkFont
from light_scrollable import LightScrollableWidget


class LightTable(LightScrollableWidget):
    LIGHT_BLUE_TAG_NAME = 'light_blue_background'
    LIGHT_BLUE = '#e0e8f0'
    FONT = None
    COLUMN_PADDING = 5

    def __init__(self, parent, title, columns):
        if self.FONT is None:
            self.FONT = tkFont.Font(font='TkDefaultFont')
        self._columns = columns
        self._min_column_widths = [self.FONT.measure(x) for x in self._columns]
        self._column_widths = self._min_column_widths[:]

        LightScrollableWidget.__init__(self, parent, title,
                                       lambda p: ttk.Treeview(self, columns=self._columns[1:]))
        self.widget.heading('#0', text=self._columns[0])
        for col in self._columns[1:]:
            self.widget.heading(col, text=col)
        self.widget.tag_configure(self.LIGHT_BLUE_TAG_NAME, background=self.LIGHT_BLUE)
        self.widget.configure(selectmode='none')
        self.configured_callback = self._may_resize_columns

    def data(self, data_row):
        """
        Must be overridden by derived classes. It should return a N-tuple of strings for the data in
        a given row. show_row() will call this method to get the data for display.
        :param data_row: Row of data to return
        :return: A N-tuple of string; one string per columns
        """
        raise NotImplementedError()

    def set_rows(self, rows):
        LightScrollableWidget.set_rows(self, rows)
        self._column_widths = self._min_column_widths[:]

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
        if (data_row % 2) == 0:
            kwargs = dict()
        else:
            kwargs = {'tag': self.LIGHT_BLUE_TAG_NAME}
        child_id = '.' + str(view_row)
        row_data = self.data(data_row)
        self.widget.insert(parent='', index=view_row, iid=child_id, text=str(row_data[0]),
                           values=row_data[1:], **kwargs)
        for (idx, val) in enumerate(row_data):
            new_width = self.FONT.measure(val)
            if self._column_widths[idx] < new_width:
                self._column_widths[idx] = new_width

    def refresh(self):
        self.clear_widget()
        self._update_widget_rows(None, None)
        widget_rows = self.widget_rows()
        if self.rows <= widget_rows:
            self._show(0, self.rows - 1)
            self.yscroll.set('0.0', '1.0')
        else:
            self._show(0, widget_rows - 1)
            self.yscroll.set(str(0.0), str(self.to_normalized(widget_rows)))
        self._resize_columns()

    def _resize_columns(self):
        total_req = sum(self._column_widths) + (self.COLUMN_PADDING * len(self._column_widths))
        if total_req == 0:
            return
        print 'COL_WIDTHS[%s]:' % self.__class__, self._column_widths
        widget_width = self._widget_width

        scale = max(1.0, float(widget_width) / float(total_req))

        self.widget.column('#0', width=int((self._column_widths[0] + self.COLUMN_PADDING) * scale))
        for idx in xrange(1, len(self._columns)):
            self.widget.column(self._columns[idx], width=int((self._column_widths[idx] + self.COLUMN_PADDING) * scale))

    def _may_resize_columns(self, attrs):
        if self.CONFIG_WIDTH in attrs:
            self._resize_columns()
