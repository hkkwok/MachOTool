from utils.header import IndexedHeader, Field


class IndirectSymbolIndex(Field):
    INDIRECT_SYMBOL_ABS = 0x40000000
    INDIRECT_SYMBOL_LOCAL = 0x80000000

    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            if value == self.INDIRECT_SYMBOL_ABS:
                return 'INDIRECT_SYMBOL_ABS'
            elif value == self.INDIRECT_SYMBOL_LOCAL:
                return 'INDIRECT_SYMBOL_LOCAL'
            else:
                return str(value)
        return super(IndirectSymbolIndex, self).display(header)


class IndirectSymbol(IndexedHeader):
    ENDIAN = None
    FIELDS = (
        IndirectSymbolIndex('sym_idx', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.sym_idx = None
        super(IndirectSymbol, self).__init__('IndirectSymbol', bytes_, **kwargs)
