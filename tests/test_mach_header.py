import unittest
from mach_o.headers.mach_header import MachHeader, CpuType, CpuSubType, MachHeader64


class TestMachHeader(unittest.TestCase):
    def setUp(self):
        with open('./binaries/executable.i386', 'rb') as f1:
            self.executable_i386 = f1.read()
        with open('./binaries/object.o.i386', 'rb') as f2:
            self.object_i386 = f2.read()

    def test_decode(self):
        hdr1 = MachHeader(self.executable_i386[0:28])
        self.assertEqual(MachHeader.MH_MAGIC, hdr1.magic)
        self.assertEqual(CpuType.CPU_TYPE_X86, hdr1.cputype)
        self.assertEqual(3, hdr1.cpusubtype)
        self.assertEqual(16, hdr1.ncmds)
        self.assertEqual(1060, hdr1.sizeofcmds)
        self.assertEqual('<mach_header: magic=MH_MAGIC, cputype=CPU_TYPE_I386, cpusubtype=CPU_SUBTYPE_X86_ALL, '
                         'filetype=MH_EXECUTE, ncmds=16, sizeofcmds=1060, flags=MH_TWOLEVEL,MH_PIE,'
                         'MH_NO_HEAP_EXECUTION,MH_NOUNDEFS,MH_DYLDLINK>', str(hdr1))

        hdr2 = MachHeader(self.object_i386[0:28])
        self.assertEqual(MachHeader.MH_MAGIC, hdr2.magic)
        self.assertEqual(CpuType.CPU_TYPE_X86, hdr1.cputype)
        self.assertEqual(CpuSubType.X86_SUBTYPES['CPU_SUBTYPE_X86_ALL'], hdr1.cpusubtype)
        self.assertEqual(4, hdr2.ncmds)
        self.assertEqual(312, hdr2.sizeofcmds)
        self.assertEqual('<mach_header: magic=MH_MAGIC, cputype=CPU_TYPE_I386, cpusubtype=CPU_SUBTYPE_X86_ALL, '
                         'filetype=MH_OBJECT, ncmds=4, sizeofcmds=312, flags=MH_SUBSECTIONS_VIA_SYMBOLS>', str(hdr2))


class TestMachHeader64(unittest.TestCase):
    def setUp(self):
        with open('./binaries/executable.x86_64', 'rb') as f1:
            self.executable_x86_64 = f1.read()
        with open('./binaries/object.o.x86_64', 'rb') as f2:
            self.object_x86_64 = f2.read()

    def test_decode(self):
        hdr1 = MachHeader64(self.executable_x86_64[0:32])
        self.assertEqual(MachHeader64.MH_MAGIC64, hdr1.magic)
        self.assertEqual(CpuType.ENUMS['CPU_TYPE_X86_64'], hdr1.cputype)
        self.assertEqual(CpuSubType.X86_64_SUBTYPES['CPU_SUBTYPE_X86_64_ALL'] | CpuSubType.CPU_SUBTYPE_LIB64,
                         hdr1.cpusubtype)
        self.assertEqual(16, hdr1.ncmds)
        self.assertEqual(1296, hdr1.sizeofcmds)
        self.assertEqual('<mach_header_64: magic=MH_MAGIC64, cputype=CPU_TYPE_X86_64, '
                         'cpusubtype=CPU_SUBTYPE_X86_64_ALL, filetype=MH_EXECUTE, ncmds=16, '
                         'sizeofcmds=1296, flags=MH_TWOLEVEL,MH_PIE,MH_NOUNDEFS,MH_DYLDLINK, reserved=0>', str(hdr1))

        hdr2 = MachHeader64(self.object_x86_64[0:32])
        self.assertEqual(MachHeader64.MH_MAGIC64, hdr2.magic)
        self.assertEqual(CpuType.ENUMS['CPU_TYPE_X86_64'], hdr1.cputype)
        self.assertEqual(CpuSubType.X86_64_SUBTYPES['CPU_SUBTYPE_X86_64_ALL'] | CpuSubType.CPU_SUBTYPE_LIB64,
                         hdr1.cpusubtype)
        self.assertEqual(4, hdr2.ncmds)
        self.assertEqual(512, hdr2.sizeofcmds)
        self.assertEqual('<mach_header_64: magic=MH_MAGIC64, cputype=CPU_TYPE_X86_64, '
                         'cpusubtype=CPU_SUBTYPE_X86_64_ALL, filetype=MH_OBJECT, ncmds=4, '
                         'sizeofcmds=512, flags=MH_SUBSECTIONS_VIA_SYMBOLS, reserved=0>', str(hdr2))
