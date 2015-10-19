from utils.header import Header
from mach_o.headers.mach_header import MachHeader, MachHeader64
from mach_o.headers.load_command import LoadCommandHeader
from mach_o.non_headers.cstring import Cstring
from mach_o.headers.dylib_command import DylibCommand


class Command(object):
    def __init__(self, command, action, desc, flag=None):
        self.command = command
        self.action = action
        self.desc = desc
        self.flag = flag
        if self.flag is None:
            self.flag = '-' + self.command[0]

    def match(self, line):
        return self.command.startswith(line.strip())

    def _get_tokens(self, line):
        tokens = line.split()
        if len(tokens) > 0:
            assert tokens[0].startswith(self.command)
        return tokens

    def getattr(self):
        return self.command.replace('-', '_')

    def run(self, line, cli):
        tokens = self._get_tokens(line)
        if len(tokens) == 0:
            return False
        method = getattr(cli, self.action)
        assert callable(method)
        method(*tokens[1:])


class CommandLine(object):
    COMMANDS = (
        Command('cstring', 'print_cstring', 'print all C strings', '-c'),
        Command('fat-header', 'print_fat_header', 'print the fat header', '-f'),
        Command('load-command', 'print_load_commands', 'print all load commands', '-l'),
        Command('mach-header', 'print_mach_header', 'print all mach headers', '-m'),
        Command('raw', 'print_full', 'print the complete structure of the file', '-R'),
        Command('shared-library', 'print_shared_libraries', 'print all shared libraries used', '-L'),
        Command('shared-library-table', 'print_shared_libraries_table', 'print all shared libraries used', ''),
    )

    def __init__(self, byte_range):
        self.byte_range = byte_range

    def run(self, line):
        # find all commands that match
        matches = list()
        for cmd in self.COMMANDS:
            if cmd.match(line):
                matches.append(cmd)
        num_matches = len(matches)
        if num_matches != 1:
            return matches
        else:
            # run the only matched command
            matches[0].run(line, self)

    @classmethod
    def configure_parser(cls, parser):
        for cmd in cls.COMMANDS:
            if cmd.flag is None:
                continue
            if len(cmd.flag) > 0:
                parser.add_argument(cmd.flag, '--' + cmd.command, action='store_true', help=cmd.desc)
            else:
                parser.add_argument('--' + cmd.command, action='store_true', help=cmd.desc)

    def parse_options(self, options):
        for cmd in self.COMMANDS:
            attr = getattr(options, cmd.getattr())
            if attr is True:
                cmd.run(cmd.command, self)

    def print_full(self):
        def format_element(br, start, stop, level):
            if level == 0:
                return ''
            return '%s%d-%d: %s' % (' ' * (level - 1), start, stop, str(br.data))
        print '\n'.join(self.byte_range.iterate(format_element))

    @staticmethod
    def format_header(hdr, trailing_lf=True):
        assert isinstance(hdr, Header)
        output = hdr.name + '\n  '
        output += '\n  '.join(hdr.get_fields_repr(': '))
        if trailing_lf:
            output += '\n'
        return output

    @staticmethod
    def _list_remove_all(str_list, pattern):
        return filter(lambda x: x != pattern, str_list)

    @staticmethod
    def _list_remove_empty(str_list):
        return CommandLine._list_remove_all(str_list, '')

    @staticmethod
    def _list_remove_none(list_):
        return CommandLine._list_remove_all(list_, None)

    def print_mach_header(self):
        def format_mach_header(br, start, stop, level):
            assert start is not None and stop is not None and level is not None  # get rid of pycharm warning
            if not isinstance(br.data, (MachHeader, MachHeader64)):
                return ''
            return self.format_header(br.data)
        lines = self.byte_range.iterate(format_mach_header)
        lines = self._list_remove_empty(lines)
        print '\n'.join(lines)

    def print_load_commands(self):
        def format_load_command(br, start, stop, level):
            assert start is not None and stop is not None and level is not None  # get rid of pycharm warning
            if not isinstance(br.data, LoadCommandHeader):
                return ''
            return self.format_header(br.data)
        lines = self.byte_range.iterate(format_load_command)
        lines = self._list_remove_empty(lines)
        print '\n'.join(lines)
        print '\n%d load commands' % len(lines)

    def print_cstring(self):
        def format_cstring(br, start, stop, level):
            assert start is not None and stop is not None and level is not None  # get rid of pycharm warning
            if not isinstance(br.data, Cstring):
                return ''
            return br.data.string
        lines = self.byte_range.iterate(format_cstring)
        lines = self._list_remove_empty(lines)
        n = 1
        for line in lines:
            print '%d: %s' % (n, line)
            n += 1

    def _get_shared_libraries(self):
        def filter_dylib_command(br, start, stop, level):
            assert start is not None and stop is not None and level is not None  # get rid of pycharm warning
            if not isinstance(br.data, DylibCommand):
                return None
            parent_br = br.parent
            assert parent_br is not None
            assert len(parent_br.subranges) in (2, 3)  # 3rd subrange is for optional alignment padding
            return br.data, parent_br.subranges[1].data
        subranges = self.byte_range.iterate(filter_dylib_command)
        dylib_commands = self._list_remove_none(subranges)
        return dylib_commands

    def print_shared_libraries(self):
        for (dylib_command, lc_str) in self._get_shared_libraries():
            print self.format_header(dylib_command, trailing_lf=False)
            print '  %s: %s\n' % (lc_str.desc, lc_str.value)

    def print_shared_libraries_table(self):
        print 'timestamp           current    compatib.  name'
        print '------------------- ---------- ---------- -------------------------'
        for (dylib_command, lc_str) in self._get_shared_libraries():
            print '%18s %10s %10s %s' % (
                DylibCommand.FIELDS[3].display(dylib_command),
                DylibCommand.FIELDS[4].display(dylib_command),
                DylibCommand.FIELDS[5].display(dylib_command),
                lc_str.value
            )

    def print_symbol_table(self):
        pass
