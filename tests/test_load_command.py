import unittest
from mach_o.headers.load_command import LoadCommand, LoadCommandCommand


class TestLoadCommand(unittest.TestCase):
    def setUp(self):
        with open('./binaries/executable.i386', 'rb') as f1:
            self.executable_i386 = f1.read()
        with open('./binaries/object.o.i386', 'rb') as f2:
            self.object_i386 = f2.read()
        with open('./binaries/executable.x86_64', 'rb') as f3:
            self.executable_x86_64 = f3.read()
        with open('./binaries/object.o.x86_64', 'rb') as f4:
            self.object_x86_64 = f4.read()

    def reset(self, start, stop, bytes_):
        self.start = start
        self.stop = stop
        self.bytes = bytes_

    def check_load_command(self, cmd, cmdsize):
        # Decode 8 bytes
        lc = LoadCommand(self.bytes[self.start:self.stop])

        # Check the values
        self.assertEqual(LoadCommandCommand.COMMANDS[cmd], lc.cmd)
        self.assertEqual(cmdsize, lc.cmdsize)

        # Update the pointers
        self.start += lc.cmdsize
        self.stop += lc.cmdsize

    def test_decode(self):
        # Decode the 4 LC in object.o.i386
        # Skip over 28 bytes of mach_header
        self.reset(28, 36, self.object_i386)
        self.check_load_command('LC_SEGMENT', 192)
        self.check_load_command('LC_VERSION_MIN_MACOSX', 16)
        self.check_load_command('LC_SYMTAB', 24)
        self.check_load_command('LC_DYSYMTAB', 80)

        # Decode the 16 LC in executable.i386
        self.reset(28, 36, self.executable_i386)
        self.check_load_command('LC_SEGMENT', 56)
        self.check_load_command('LC_SEGMENT', 396)
        self.check_load_command('LC_SEGMENT', 192)
        self.check_load_command('LC_SEGMENT', 56)
        self.check_load_command('LC_DYLD_INFO_ONLY', 48)
        self.check_load_command('LC_SYMTAB', 24)
        self.check_load_command('LC_DYSYMTAB', 80)
        self.check_load_command('LC_LOAD_DYLINKER', 28)
        self.check_load_command('LC_UUID', 24)
        self.check_load_command('LC_VERSION_MIN_MACOSX', 16)
        self.check_load_command('LC_SOURCE_VERSION', 16)
        self.check_load_command('LC_MAIN', 24)
        self.check_load_command('LC_LOAD_DYLIB', 52)
        self.check_load_command('LC_FUNCTION_STARTS', 16)
        self.check_load_command('LC_DATA_IN_CODE', 16)
        self.check_load_command('LC_DYLIB_CODE_SIGN_DRS', 16)

        # Decode the 4 LC in object.o.x86_64
        self.reset(32, 40, self.object_x86_64)
        self.check_load_command('LC_SEGMENT_64', 392)
        self.check_load_command('LC_VERSION_MIN_MACOSX', 16)
        self.check_load_command('LC_SYMTAB', 24)
        self.check_load_command('LC_DYSYMTAB', 80)

        # Decode the 16 LC in executable.x86_64
        self.reset(32, 40, self.executable_x86_64)
        self.check_load_command('LC_SEGMENT_64', 72)
        self.check_load_command('LC_SEGMENT_64', 552)
        self.check_load_command('LC_SEGMENT_64', 232)
        self.check_load_command('LC_SEGMENT_64', 72)
        self.check_load_command('LC_DYLD_INFO_ONLY', 48)
        self.check_load_command('LC_SYMTAB', 24)
        self.check_load_command('LC_DYSYMTAB', 80)
        self.check_load_command('LC_LOAD_DYLINKER', 32)
        self.check_load_command('LC_UUID', 24)
        self.check_load_command('LC_VERSION_MIN_MACOSX', 16)
        self.check_load_command('LC_SOURCE_VERSION', 16)
        self.check_load_command('LC_MAIN', 24)
        self.check_load_command('LC_LOAD_DYLIB', 56)
        self.check_load_command('LC_FUNCTION_STARTS', 16)
        self.check_load_command('LC_DATA_IN_CODE', 16)
        self.check_load_command('LC_DYLIB_CODE_SIGN_DRS',16)