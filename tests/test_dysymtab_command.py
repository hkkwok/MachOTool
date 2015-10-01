import unittest
from mach_o.headers.dysymtab_command import DysymtabCommand
from mach_o.headers.load_command import LoadCommandCommand


class TestDysymTabCommand(unittest.TestCase):
    def setUp(self):
        with open('./binaries/executable.i386', 'rb') as f1:
            self.executable_i386 = f1.read()
        with open('./binaries/object.o.i386', 'rb') as f2:
            self.object_i386 = f2.read()
        with open('./binaries/executable.x86_64', 'rb') as f3:
            self.executable_x86_64 = f3.read()
        with open('./binaries/object.o.x86_64', 'rb') as f4:
            self.object_x86_64 = f4.read()

    def check_dysymtab_command(self, dtc, ilocalsym, nlocalsym, iextdefsym, nextdefsym,
                               iundefsym, nundefsym, tocoff, ntoc, modtaboff, nmodtab,
                               extrefsymoff, nextrefsyms, indirectsymoff, nindirectsyms,
                               extreloff, nextrel, locreloff, nlocrel):
        self.assertEqual(LoadCommandCommand.COMMANDS['LC_DYSYMTAB'], dtc.cmd)
        self.assertEqual(ilocalsym, dtc.ilocalsym)
        self.assertEqual(nlocalsym, dtc.nlocalsym)
        self.assertEqual(iextdefsym, dtc.iextdefsym)
        self.assertEqual(nextdefsym, dtc.nextdefsym)
        self.assertEqual(iundefsym, dtc.iundefsym)
        self.assertEqual(nundefsym, dtc.nundefsym)
        self.assertEqual(tocoff, dtc.tocoff)
        self.assertEqual(ntoc, dtc.ntoc)
        self.assertEqual(modtaboff, dtc.modtaboff)
        self.assertEqual(nmodtab, dtc.nmodtab)
        self.assertEqual(extrefsymoff, dtc.extrefsymoff)
        self.assertEqual(nextrefsyms, dtc.nextrefsyms)
        self.assertEqual(indirectsymoff, dtc.indirectsymoff)
        self.assertEqual(nindirectsyms, dtc.nindirectsyms)
        self.assertEqual(extreloff, dtc.extreloff)
        self.assertEqual(nextrel, dtc.nextrel)
        self.assertEqual(locreloff, dtc.locreloff)
        self.assertEqual(nlocrel, dtc.nlocrel)

    def test_decode(self):
        dtc = DysymtabCommand(self.object_i386[260:340])
        self.check_dysymtab_command(dtc,
                                    ilocalsym=0,
                                    nlocalsym=0,
                                    iextdefsym=0,
                                    nextdefsym=1,
                                    iundefsym=1,
                                    nundefsym=1,
                                    tocoff=0,
                                    ntoc=0,
                                    modtaboff=0,
                                    nmodtab=0,
                                    extrefsymoff=0,
                                    nextrefsyms=0,
                                    indirectsymoff=0,
                                    nindirectsyms=0,
                                    extreloff=0,
                                    nextrel=0,
                                    locreloff=0,
                                    nlocrel=0)

        dtc = DysymtabCommand(self.executable_i386[800:880])
        self.check_dysymtab_command(dtc,
                                    ilocalsym=0,
                                    nlocalsym=0,
                                    iextdefsym=0,
                                    nextdefsym=2,
                                    iundefsym=2,
                                    nundefsym=2,
                                    tocoff=0,
                                    ntoc=0,
                                    modtaboff=0,
                                    nmodtab=0,
                                    extrefsymoff=0,
                                    nextrefsyms=0,
                                    indirectsymoff=8364,
                                    nindirectsyms=4,
                                    extreloff=0,
                                    nextrel=0,
                                    locreloff=0,
                                    nlocrel=0)

        dtc = DysymtabCommand(self.object_x86_64[464:544])
        self.check_dysymtab_command(dtc,
                                    ilocalsym=0,
                                    nlocalsym=1,
                                    iextdefsym=1,
                                    nextdefsym=1,
                                    iundefsym=2,
                                    nundefsym=1,
                                    tocoff=0,
                                    ntoc=0,
                                    modtaboff=0,
                                    nmodtab=0,
                                    extrefsymoff=0,
                                    nextrefsyms=0,
                                    indirectsymoff=0,
                                    nindirectsyms=0,
                                    extreloff=0,
                                    nextrel=0,
                                    locreloff=0,
                                    nlocrel=0)

        dtc = DysymtabCommand(self.executable_x86_64[1032:1112])
        self.check_dysymtab_command(dtc,
                                    ilocalsym=0,
                                    nlocalsym=0,
                                    iextdefsym=0,
                                    nextdefsym=2,
                                    iundefsym=2,
                                    nundefsym=2,
                                    tocoff=0,
                                    ntoc=0,
                                    modtaboff=0,
                                    nmodtab=0,
                                    extrefsymoff=0,
                                    nextrefsyms=0,
                                    indirectsymoff=8384,
                                    nindirectsyms=4,
                                    extreloff=0,
                                    nextrel=0,
                                    locreloff=0,
                                    nlocrel=0)
