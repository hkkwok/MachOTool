import unittest
from mach_o.headers.segment_command import SegmentCommand, SegmentCommand64
from mach_o.headers.load_command import LoadCommandCommand


class TestSegmentCommand(unittest.TestCase):
    def setUp(self):
        with open('./binaries/executable.i386', 'rb') as f1:
            self.executable_i386 = f1.read()
        with open('./binaries/object.o.i386', 'rb') as f2:
            self.object_i386 = f2.read()

    def reset(self,  start, stop, bytes_):
        self.start = start
        self.stop = stop
        self.bytes = bytes_

    def check_segment_command(self, cmdsize, segname, vmaddr, vmsize, fileoff,
                              filesize, maxprot, initprot, nsects, flags):
        sc = SegmentCommand(self.bytes[self.start:self.stop])
        self.assertEqual(LoadCommandCommand.COMMANDS['LC_SEGMENT'], sc.cmd)
        self.assertEqual(cmdsize, sc.cmdsize)
        self.assertEqual(segname, sc.segname)
        self.assertEqual(vmaddr, sc.vmaddr)
        self.assertEqual(vmsize, sc.vmsize)
        self.assertEqual(fileoff, sc.fileoff)
        self.assertEqual(filesize, sc.filesize)
        self.assertEqual(maxprot, sc.maxprot)
        self.assertEqual(initprot, sc.initprot)
        self.assertEqual(nsects, sc.nsects)
        self.assertEqual(flags, sc.flags)

        self.start += cmdsize
        self.stop += cmdsize

    @staticmethod
    def padded_string(s, length):
        return s + ('\x00' * (length - len(s)))

    def test_decode(self):
        # Decode object.o.i386
        self.reset(28, 84, self.object_i386)
        self.check_segment_command(192, self.padded_string('', 16), 0x0, 0x4b, 340, 75, 0x7, 0x7, 2, 0x0)

        # Decode executable.i386
        self.reset(28, 84, self.executable_i386)
        self.check_segment_command(56, self.padded_string('__PAGEZERO', 16), 0x0, 0x1000, 0, 0, 0x0, 0x0, 0, 0x0)
        self.check_segment_command(396, self.padded_string('__TEXT', 16), 0x1000, 0x1000, 0, 4096, 0x7, 0x5, 5, 0x0)
        self.check_segment_command(192, self.padded_string('__DATA', 16), 0x2000, 0x1000, 4096, 4096, 0x7, 0x3, 2, 0x0)
        self.check_segment_command(56, self.padded_string('__LINKEDIT', 16), 0x3000, 0x1000,
                                   8192, 244, 0x7, 0x1, 0, 0x0)


class TestSegmentCommand64(unittest.TestCase):
    def setUp(self):
        with open('./binaries/executable.x86_64', 'rb') as f1:
            self.executable_x86_64 = f1.read()
        with open('./binaries/object.o.x86_64', 'rb') as f2:
            self.object_x86_64 = f2.read()

    def reset(self,  start, stop, bytes_):
        self.start = start
        self.stop = stop
        self.bytes = bytes_

    def check_segment_command(self, cmdsize, segname, vmaddr, vmsize, fileoff,
                              filesize, maxprot, initprot, nsects, flags):
        sc = SegmentCommand64(self.bytes[self.start:self.stop])
        self.assertEqual(LoadCommandCommand.COMMANDS['LC_SEGMENT_64'], sc.cmd)
        self.assertEqual(cmdsize, sc.cmdsize)
        self.assertEqual(segname, sc.segname)
        self.assertEqual(vmaddr, sc.vmaddr)
        self.assertEqual(vmsize, sc.vmsize)
        self.assertEqual(fileoff, sc.fileoff)
        self.assertEqual(filesize, sc.filesize)
        self.assertEqual(maxprot, sc.maxprot)
        self.assertEqual(initprot, sc.initprot)
        self.assertEqual(nsects, sc.nsects)
        self.assertEqual(flags, sc.flags)

        self.start += cmdsize
        self.stop += cmdsize

    @staticmethod
    def padded_string(s, length):
        return s + ('\x00' * (length - len(s)))

    def test_decode(self):
        # Decode object.o.x86_64
        self.reset(32, 104, self.object_x86_64)
        self.check_segment_command(392, self.padded_string('', 16), 0x0, 0xa8, 544, 168, 0x7, 0x7, 4, 0x0)

        # Decode executable.x86_64
        self.reset(32, 104, self.executable_x86_64)
        self.check_segment_command(72, self.padded_string('__PAGEZERO', 16), 0x0, 0x100000000, 0, 0, 0x0, 0x0, 0, 0x0)
        self.check_segment_command(552, self.padded_string('__TEXT', 16), 0x100000000, 0x1000,
                                   0, 4096, 0x7, 0x5, 6, 0x0)
        self.check_segment_command(232, self.padded_string('__DATA', 16), 0x100001000, 0x1000,
                                   4096, 4096, 0x7, 0x3, 2, 0x0)
        self.check_segment_command(72, self.padded_string('__LINKEDIT', 16), 0x100002000, 0x1000,
                                   8192, 264, 0x7, 0x1, 0, 0x0)
