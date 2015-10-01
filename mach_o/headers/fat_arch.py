from utils.header import Header, Field
from cpu_type import CpuType, CpuSubType


class FatArch(Header):
    ENDIAN = True  # big endian
    FIELDS = (CpuType('cputype', 'I'),
              CpuSubType('cpusubtype', 'cputype', 'I'),
              Field('offset', 'I'),
              Field('size', 'I'),
              Field('align', 'I'))

    def __init__(self, bytes_=None, **kwargs):
        self.cputype = None
        self.cpusubtype = None
        self.offset = None
        self.size = None
        self.align = None
        super(FatArch, self).__init__('fat_arch', bytes_, **kwargs)
