## Introduction
***

Mach-O Tool is meant to be a portable tool for analyzing Mach-O binaries. It is written entirely
in Python and should work with any standard Python 2.7 installation without additional packages.
(The GUI part requires Tkinter which should be a standard package in most platforms.)

It contains 3 components:

1. A Mach-O parsing library. Initial version supports parsing for most common fields / headers.
   The long term goal is to parse all documented fields / headers. The library can be used
   to build other Mach-O manipulation tools.

2. A command-line tool very similar to otool, dyldinfo and nm. It also has an interactive mode.
3. A GUI tool for interactive binary analysis.

<br/><br/>
  
## Command-Line Mode
***

To see available options, just do: ./machotool.py -h

usage: machotool.py [-h] [-i | -g] [-v] [-c] [-f] [-l] [-m] [-R] [-L]
                    [--shared-library-table]
                    [file]

....


Some of these parameters are identical to otool's. For example, to list all load commands of a binary:

    ./machotool.py -l /bin/ls

    segment_command_64
      cmd: LC_SEGMENT_64
      cmdsize: 72
      segname: \__PAGEZERO
      vmaddr: 0x0
      vmsize: 4294967296
      fileoff: 0
      filesize: 0
      maxprot: 0
      initprot: 0
      nsects: 0
      flags: 0x0

    segment_command_64
      cmd: LC_SEGMENT_64
      cmdsize: 552
      segname: \__TEXT
      vmaddr: 0x100000000
      vmsize: 20480
      fileoff: 0
      filesize: 20480
      maxprot: 7
      initprot: 5
      nsects: 6
      flags: 0x0

    ...

To list all required shared libraries:

    ./machotool -L /bin/ls

    dylib_command
      cmd: LC_LOAD_DYLIB
      cmdsize: 48
      dylib_name_offset: 24
      dylib_timestamp: 1969-12-31 16:00:02
      dylib_current_version: 1.0.0
      dylib_compatiblity_version: 1.0.0
      dylib_name: /usr/lib/libutil.dylib

    dylib_command
      cmd: LC_LOAD_DYLIB
      cmdsize: 56
      dylib_name_offset: 24
      dylib_timestamp: 1969-12-31 16:00:02
      dylib_current_version: 5.4.0
      dylib_compatiblity_version: 5.4.0
      dylib_name: /usr/lib/libncurses.5.4.dylib

    dylib_command
      cmd: LC_LOAD_DYLIB
      cmdsize: 56
      dylib_name_offset: 24
      dylib_timestamp: 1969-12-31 16:00:02
      dylib_current_version: 1225.1.1
      dylib_compatiblity_version: 1.0.0
      dylib_name: /usr/lib/libSystem.B.dylib

<br/><br/>

## Interactive Mode
***
If you need to see various fields of a binary, it may be faster to enter
interative mode which analyzes the binary once and allows you to enter
various commands to see various fields.

To run in interactive mode, use -i flag:

./machotool.py -i /bin/ls

The commands are the same as the long options in the command-line mode
without the '--' prefix.

For example, the equivalent command for '-m' option is 'mach-header'

<br/><br/>

## GUI Mode
***
To run GUI mode, use -g flag:

./machotool.py -g /bin/ls

There 3 tabs or windows:

1. <b>Decode window</b> - Provide a hierarchical view of all fields in a binary.
2. <b>String window</b> - List all strings of various kinds. (E.g. c string and ObjC method names.)
3. <b>Symbol window</b> - List all symbols coalesced with their sections (if available) and attributes.
