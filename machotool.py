#!/usr/bin/env python
from mach_o.mach_o import MachO
from mach_o.fat import Fat
from mach_o.headers.fat_header import FatHeader
from mach_o.headers.mach_header import MachHeader, MachHeader64
from utils.bytes import Bytes
from utils.byte_range import ByteRange
from utils.ansi_text import AnsiText
from utils.progress_indicator import ProgressIndicator
from ui.command_line import CommandLine
from ui.gui.gui import Gui

import argparse
import sys
import Tkinter as Tk


def print_element(br, start, stop, level):
    if level == 0:
        return ''
    return '%s%d-%d: %s' % (' ' * (level - 1), start, stop, str(br.data))


def main():
    # Parse command-line option
    parser = argparse.ArgumentParser()

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-i', '--interactive', action='store_true', help='run in interactive (command-line) mode')
    group.add_argument('-g', '--gui', action='store_true', help='run in graphical mode')
    parser.add_argument('-v', '--verbose', action='store_true', default=False, help='verbose logs')

    parser.add_argument('file', nargs='?', help='binary file to be analyzed')

    # Add all supported commands as option flags
    CommandLine.configure_parser(parser)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    else:
        options = parser.parse_args()

    ProgressIndicator.ENABLED = options.verbose

    if options.gui:
        AnsiText.ENABLE_COLOR = False
        root = Tk.Tk()
        gui = Gui(root)
        if options.file is not None:
            gui.load_file(options.file)
        try:
            root.mainloop()
        except KeyboardInterrupt:
            print '\nGoodBye!'
        root.destroy()
    else:
        # Read and parse the file
        bytes_ = Bytes(options.file)
        byte_range = ByteRange(0, len(bytes_), data=bytes_)

        # Determine if the first header is a fat header, mach header or neither
        if MachHeader.is_valid_header(bytes_.bytes) or MachHeader64.is_valid_header(bytes_.bytes):
            mach_o = MachO(byte_range)
            byte_range.data = mach_o
        elif FatHeader.is_valid_header(bytes_.bytes):
            fat = Fat(byte_range)
            byte_range.data = fat
        else:
            print 'ERROR: Cannot find neither fat nor mach header in the beginning of the binary.'
            sys.exit(1)

        cli = CommandLine(byte_range)
        cli.parse_options(options)
        while options.interactive:
            try:
                line = raw_input('>> ')
                cli.run(line)
            except (EOFError, KeyboardInterrupt):
                options.interactive = False
                print '\nGoodbye!'

if __name__ == '__main__':
    main()
