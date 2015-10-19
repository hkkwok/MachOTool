try:
    # Python 2
    import Tkinter as Tk
    import tkFont as tkFont
    import ttk
    import tkFileDialog as filedialog
except ImportError:
    # Python 3
    import tkinter as Tk
    import tkinter.ttk as ttk
    import tkinter.font as tkFont
    import tkinter.filedialog as filedialog
from window_tab import WindowTab
from decode_window import DecodeWindow
from string_window import StringWindow
from symbol_window import SymbolWindow
from utils.byte_range import ByteRange, Bytes
from mach_o.headers.mach_header import MachHeader, MachHeader64
from mach_o.fat import FatHeader, Fat
from mach_o.mach_o import MachO

from utils.header import IndexedHeader


class Gui(object):
    TITLE = 'MachOTool'
    WINDOWS = (DecodeWindow, StringWindow, SymbolWindow)

    def __init__(self, parent):
        self.parent = parent
        self.set_subtitle(None)
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(side=Tk.TOP, fill=Tk.BOTH, expand=True)

        self.tabs = list()
        self.visible_tabs = None
        self.view_items = None

        for cls in self.WINDOWS:
            self.create_tab(cls)
        for tab in self.tabs:
            self.notebook.add(tab, text=tab.TITLE)
        self.visible_tabs = self.tabs[:]

        # Add menus
        self.menu_bar = Tk.Menu(self.parent)
        self._add_menu('File', (MenuCommand('Open', self.open, underline=0, accelerator='Ctrl-O'),
                                MenuCommand('Quit', self.quit, underline=0, accelerator='Ctrl-Q')))
        self._setup_view_menu_items()
        self._add_menu('Views', self.view_items)
        self.parent.config(menu=self.menu_bar)

        self.byte_range = None
        self.bytes = None

        self.notebook.bind('<<NotebookTabChanged>>', self.tab_selected)
        self.parent.bind_all('<Control-o>', self.open2)
        self.parent.bind_all('<Control-q>', self.quit2)

    def create_tab(self, cls):
        assert issubclass(cls, WindowTab)
        assert callable(cls)
        tab = cls(self.notebook)
        self.tabs.append(tab)

    def _setup_view_menu_items(self):
        self.view_items = list()
        for cls in self.WINDOWS[1:]:  # skip decode window which is always visible
            item = MenuCheckButton(cls.TITLE + ' view', self.update_tabs, 1)
            self.view_items.append(item)

    def set_subtitle(self, subtitle):
        if subtitle is None:
            title = self.TITLE
        else:
            title = '%s [%s]' % (self.TITLE, subtitle)
        self.parent.wm_title(title)

    def load_file(self, file_path):
        # Read and parse the file
        bytes_ = Bytes(file_path)
        byte_range = ByteRange(0, len(bytes_), data=bytes_)

        IndexedHeader.reset_indices()

        # Determine if the first header is a fat header, mach header or neither
        if MachHeader.is_valid_header(bytes_.bytes) or MachHeader64.is_valid_header(bytes_.bytes):
            mach_o = MachO(byte_range)
            byte_range.data = mach_o
        elif FatHeader.is_valid_header(bytes_.bytes):
            fat = Fat(byte_range)
            byte_range.data = fat
        else:
            print 'ERROR: Cannot find neither fat nor mach header in the beginning of the binary.'
            return
        self.load(byte_range, bytes_)
        self.set_subtitle(file_path)

    def load(self, byte_range, bytes_):
        selected = self.notebook.select()
        # Do not update all notebook pages in order to speed up load time.
        # Lazy initializes every page
        visible_ids = self.notebook.tabs()
        for index in xrange(len(self.visible_tabs)):
            tab = self.visible_tabs[index]
            if visible_ids[index] == selected:
                tab.load(byte_range, bytes_)
            else:
                tab.clear()
        self.byte_range = byte_range
        self.bytes = bytes_
        self.parent.update_idletasks()

    def _selected_tab(self):
        selected = self.notebook.select()
        for (idx, tab) in enumerate(self.tabs):
            if tab.widget_id() == selected:
                return tab
        return None

    def tab_selected(self, event):
        assert event is not None  # get rid of pycharm warning
        selected_tab = self._selected_tab()
        if not selected_tab.is_loaded():
            selected_tab.load(self.byte_range, self.bytes)

    def _add_menu(self, name, items):
        menu = Tk.Menu(self.menu_bar, tearoff=0)
        for item in items:
            item.add(menu)
        self.menu_bar.add_cascade(label=name, menu=menu)

    def open(self):
        file_path = filedialog.askopenfilename(parent=self.parent)
        if file_path != '':
            self.load_file(file_path)

    def open2(self, event):
        assert event is not None
        self.open()

    def quit(self):
        self.parent.quit()
        print 'Goodbye!\n'

    def quit2(self, event):
        assert event is not None
        self.quit()

    def update_tabs(self):
        diffs = dict()
        for vtab in self.visible_tabs:
            diffs[vtab] = -1
        diffs[self.tabs[0]] += 1
        new_visible_tabs = [self.tabs[0]]  # decode window is never hidden
        for (tab_idx, tab) in enumerate(self.tabs[1:], start=1):
            tab = self.tabs[tab_idx]
            if self.view_items[tab_idx - 1].state():
                if tab not in diffs:
                    diffs[tab] = 1
                else:
                    diffs[tab] += 1
                new_visible_tabs.append(tab)

        for (tab, change) in diffs.items():
            if change == 0:
                continue
            elif change == +1:
                self.notebook.add(tab)
            elif change == -1:
                self.notebook.hide(tab.widget_id())
            else:
                assert False  # shouldn't happen

        self.visible_tabs = new_visible_tabs


class MenuCommand(object):
    def __init__(self, description, command, **kwargs):
        self.description = description
        assert callable(command)
        self.command = command
        self.kwargs = kwargs

    def add(self, menu):
        menu.add_command(label=self.description, command=self.command, **self.kwargs)


class MenuCheckButton(MenuCommand):
    def __init__(self, description, command, initial_value):
        super(MenuCheckButton, self).__init__(description, command)
        self._state = Tk.IntVar()
        if initial_value:
            self._state.set(1)
        else:
            self._state.set(0)

    def add(self, menu):
        menu.add_checkbutton(label=self.description, command=self.command, variable=self._state)

    def state(self, new_state=None):
        if new_state is not None:
            if new_state:
                self._state.set(1)
            else:
                self._state.set(0)
        return bool(self._state.get())
