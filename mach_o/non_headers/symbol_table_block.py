from utils.header import Header, NonEncodingField
from utils.commafy import commafy


class SymbolTableBase(Header):
    FIELDS =(
        NonEncodingField('desc'),
    )

    def __init__(self, entry_type, num_entries=None):
        if num_entries is not None:
            desc = '%s %s' % (commafy(num_entries), entry_type)
        else:
            desc = entry_type
        super(SymbolTableBase, self).__init__('SymbolTable: %s' % desc, desc=desc)


class SymbolTable(SymbolTableBase):
    SYM_INDEX = 0
    N_STRX = 1
    N_TYPE = 2
    N_SECT = 3
    N_DESC = 4
    N_VALUE = 5
    SYM_NAME = 6

    def __init__(self, num_symbols):
        super(SymbolTable, self).__init__('symbol entries', num_symbols)
        self.symbols = list()

    def add(self, nlist):
        idx = len(self.symbols)
        self.symbols.append((idx, nlist.n_strx, nlist.n_type, nlist.n_sect, nlist.n_desc, nlist.n_value, None))

    def correlate_string_table(self, sym_str_tab):
        assert isinstance(sym_str_tab, SymbolStringTable)
        for idx in xrange(len(self.symbols)):
            n_strx = self.symbols[idx][self.N_STRX]
            if n_strx == 0:
                continue
            sym_name = sym_str_tab.symbol_strings.get(n_strx, None)
            if sym_name is not None:
                self.symbols[idx] = self.symbols[idx][:self.SYM_NAME] + (sym_name,)

    def filter(self, pattern=None):
        if pattern is None:
            return range(len(self.symbols))

        indices = list()
        for (sym_idx, (index, n_strx, n_type, n_sect, n_desc, n_value, symbol_name)) in enumerate(self.symbols):
            if pattern in symbol_name:
                indices.append(sym_idx)
        return indices


class SymbolStringTable(SymbolTableBase):
    def __init__(self):
        super(SymbolStringTable, self).__init__('string table')
        self.symbol_strings = dict()

    def add(self, n_strx, s):
        self.symbol_strings[n_strx] = s


class IndirectSymbolTable(SymbolTableBase):
    def __init__(self, num_indirect_symbols):
        super(IndirectSymbolTable, self).__init__('indirect symbols', num_indirect_symbols)


class ExtRefSymbolTable(SymbolTableBase):
    def __init__(self, num_ext_ref):
        super(ExtRefSymbolTable, self).__init__('external references', num_ext_ref)
