from utils.header import NullTerminatedStringField
from mach_o.headers.nlist import Nlist64


class SymbolMachOInfo(object):
    """
    SymbolMachOInfo is a helper class that manages the information to be presented
    in SymbolWindow. There is one MachOInfo object per MachO in a binary.
    It contains a list of symbol tables and sections (for that MachO). It also
    holds the filtering results. The UI objects above only need to:

    1. Create a MachOInfo object for each mach_header header.
    2. Add a section object (to the MachOInfo object) for each section header.
    3. Add a symbol table object for each symtab_command header.
    4. Filter with the given symbol pattern.
    5. Get a symbol given an index from 0 to self.num_matched - 1.
    """
    def __init__(self, desc):
        self.desc = desc
        self._sections = list()
        # There should be only one symbol table per Mach-O but I cannot find documentation that
        # guarantee that constraint. So, if there are multiple LC_SYMTAB_COMMAND, we need to keep
        # a list of symbol tables.
        self._symbol_tables = list()
        self._filter_mappings = None
        self.num_matched = None

    def add_symbol_table(self, symbol_table):
        self._symbol_tables.append(symbol_table)

    def add_section(self, section):
        self._sections.append(section)

    def filter(self, pattern):
        self._filter_mappings = list()
        self.num_matched = 0
        for symbol_table in self._symbol_tables:
            indices = symbol_table.filter(pattern)
            self._filter_mappings.append(indices)
            self.num_matched += len(indices)
        return self.num_matched

    def num_symbols(self):
        return sum([len(st.symbols) for st in self._symbol_tables], 0)

    def symbol(self, matched_idx):
        assert 0 <= matched_idx < self.num_matched
        table_idx = 0
        section_desc = ''
        for mapping in self._filter_mappings:
            mapping_size = len(mapping)
            if matched_idx >= mapping_size:
                matched_idx -= mapping_size
                table_idx += 1
                continue
            (index, n_strx, n_type, n_sect, n_desc, n_value, symbol_name) = \
                self._symbol_tables[table_idx].symbols[mapping[matched_idx]]
            nlist = Nlist64(index=index,
                            n_strx=n_strx,
                            n_type=n_type,
                            n_sect=n_sect,
                            n_desc=n_desc,
                            n_value=n_value)
            if nlist.n_sect != 0:
                this_section = self._sections[nlist.n_sect]
                section_desc = '%s, %s' % \
                               (NullTerminatedStringField.get_string(this_section.segname),
                                NullTerminatedStringField.get_string(this_section.sectname))
            return nlist, symbol_name, section_desc
        assert False  # should never get here
