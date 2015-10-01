import unittest
from mach_o.headers.symtab_command import SymtabCommand
from mach_o.headers.load_command import LoadCommandCommand


class TestSymtabCommand(unittest.TestCase):
    def setUp(self):
        with open('./binaries/executable.i386', 'rb') as f1:
            self.executable_i386 = f1.read()
        with open('./binaries/object.o.i386', 'rb') as f2:
            self.object_i386 = f2.read()
        with open('./binaries/executable.x86_64', 'rb') as f3:
            self.executable_x86_64 = f3.read()
        with open('./binaries/object.o.x86_64', 'rb') as f4:
            self.object_x86_64 = f4.read()

    def check_symtab_command(self, sc, symoff, nsyms, stroff, strsize):
        self.assertEqual(LoadCommandCommand.COMMANDS['LC_SYMTAB'], sc.cmd)
        self.assertEqual(24, sc.cmdsize)
        self.assertEqual(symoff, sc.symoff)
        self.assertEqual(nsyms, sc.nsyms)
        self.assertEqual(stroff, sc.stroff)
        self.assertEqual(strsize, sc.strsize)

    def test_decode(self):
        # Decode LC_SYMTAB in executable.i386
        sc = SymtabCommand(self.executable_i386[776:800])
        self.check_symtab_command(sc, 8316, 4, 8380, 56)

        # Decode LC_SYMTAB in object.o.i386
        sc = SymtabCommand(self.object_i386[236:260])
        self.check_symtab_command(sc, 440, 2, 464, 16)

        # Decode LC_SYMTAB in executable.x86_64
        sc = SymtabCommand(self.executable_x86_64[1008:1032])
        self.check_symtab_command(sc, 8320, 4, 8400, 56)

        # Decode LC_SYMTAB in object.o.x86_64
        sc = SymtabCommand(self.object_x86_64[440:464])
        self.check_symtab_command(sc, 736, 3, 784, 24)
