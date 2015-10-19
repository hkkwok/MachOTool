from headers.fat_header import FatHeader
from headers.fat_arch import FatArch
from mach_o import MachO
from utils.bytes_range_parser import BytesRangeParser


class Fat(BytesRangeParser):
    def __init__(self, fat_br):
        super(Fat, self).__init__(fat_br)
        self.start = 0
        self.current = 0
        self.cmd_size = len(fat_br)

        # Create the fat header
        hdr_size = FatHeader.get_size()
        self.fat_header = FatHeader(fat_br.bytes(0, hdr_size))
        self.add_subrange(self.fat_header, hdr_size)

        # Create all fat arch headers
        hdr_size = FatArch.get_size()
        self.archs = list()
        for arch_idx in xrange(self.fat_header.nfat_arch):
            bytes_ = self._get_bytes(hdr_size)
            fat_arch = FatArch(bytes_)
            self.add_subrange(fat_arch, hdr_size)
            self.archs.append(fat_arch)

        # Create Mach-O section for each architecture
        for arch_idx in xrange(self.fat_header.nfat_arch):
            fat_arch = self.archs[arch_idx]
            mach_o_br = self.byte_range.add_subrange(fat_arch.offset, fat_arch.size)
            macho = MachO(mach_o_br)
            mach_o_br.data = macho

    def __repr__(self):
        out = '<Fat:\n'
        out += '  ' + str(self.fat_header) + '\n'
        for fat_arch in self.archs:
            out += '  ' + str(fat_arch) + '\n'
        out += '>'
        return out
