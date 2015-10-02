from utils.header import IndexedHeader, Field, HexField
from utils.mapping import Mapping


class NType(HexField):
    # From mach-o/loader.h
    N_STAB = 0xe0
    N_PEXT = 0x10
    N_TYPE = 0x0e
    N_EXT = 0x01

    # N_TYPE values - from mach-o/loader.h
    NTypes = Mapping({
        'N_UNDF': 0x0,
        'N_ABS': 0x2,
        'N_SECT': 0xe,
        'N_PBUD': 0xc,
        'N_INDR': 0xa,
    })

    # Stab values - from mach-o/stab.h
    NStabs = Mapping({
        'N_GSYM':  0x20,    # global symbol: name,,NO_SECT,type,0
        'N_FNAME': 0x22,    # procedure name (f77 kludge): name,,NO_SECT,0,0
        'N_FUN':   0x24,    # procedure: name,,n_sect,linenumber,address
        'N_STSYM': 0x26,    # static symbol: name,,n_sect,type,address
        'N_LCSYM': 0x28,    # .lcomm symbol: name,,n_sect,type,address
        'N_BNSYM': 0x2e,    # begin nsect sym: 0,,n_sect,0,address
        'N_OPT':   0x3c,    # emitted with gcc2_compiled and in gcc source
        'N_RSYM':  0x40,    # register sym: name,,NO_SECT,type,register
        'N_SLINE': 0x44,    # src line: 0,,n_sect,linenumber,address
        'N_ENSYM': 0x4e,    # end nsect sym: 0,,n_sect,0,address
        'N_SSYM':  0x60,    # structure elt: name,,NO_SECT,type,struct_offset
        'N_SO':    0x64,    # source file name: name,,n_sect,0,address
        'N_OSO':   0x66,    # object file name: name,,0,0,st_mtime
        'N_LSYM':  0x80,    # local sym: name,,NO_SECT,type,offset
        'N_BINCL': 0x82,    # include file beginning: name,,NO_SECT,0,sum
        'N_SOL':   0x84,    # #included file name: name,,n_sect,0,address
        'N_PARAMS':  0x86,  # compiler parameters: name,,NO_SECT,0,0
        'N_VERSION': 0x88,  # compiler version: name,,NO_SECT,0,0
        'N_OLEVEL':  0x8A,  # compiler -O level: name,,NO_SECT,0,0
        'N_PSYM':  0xa0,    # parameter: name,,NO_SECT,type,offset
        'N_EINCL': 0xa2,    # include file end: name,,NO_SECT,0,0
        'N_ENTRY': 0xa4,    # alternate entry: name,,n_sect,linenumber,address
        'N_LBRAC': 0xc0,    # left bracket: 0,,NO_SECT,nesting level,address
        'N_EXCL':  0xc2,    # deleted include file: name,,NO_SECT,0,sum
        'N_RBRAC': 0xe0,    # right bracket: 0,,NO_SECT,nesting level,address
        'N_BCOMM': 0xe2,    # begin common: name,,NO_SECT,0,0
        'N_ECOMM': 0xe4,    # end common: name,,n_sect,0,0
        'N_ECOML': 0xe8,    # end common (local name): 0,,n_sect,0,address
        'N_LENG':  0xfe,    # second stab entry with length information
    })

    def _is_stab(self, value):
        return (value & self.N_STAB) != 0

    def validate(self, header):
        value = self._get_value(header)
        if self._is_stab(value):
            # Check for a valid stab value
            return self.NStabs.has_value(value)
        else:
            # Check for a valid n_type value
            return self.NTypes.has_value(value & self.N_TYPE)

    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            if self._is_stab(value):
                return self.NStabs.key(value)
            else:
                attrs = list()
                attrs.append(self.NTypes.key(value & self.N_TYPE))
                if value & self.N_PEXT:
                    attrs.append('N_PEXT')
                if value & self.N_EXT:
                    attrs.append('N_EXT')
                return ','.join(attrs)
        return super(NType, self).display(header)

    def type(self, header):
        value = self._get_value(header)
        if self._is_stab(value):
            return self.NStabs.key(value)
        return self.NTypes.key(value & self.N_TYPE)


class NSect(Field):
    NO_SECT = 0

    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            if value == self.NO_SECT:
                return 'NO_SECT'
            else:
                return str(value)
        return super(NSect, self).display(header)


class NDesc(Field):
    REFERENCE_TYPE = 0x7

    REFERENCE_FLAGS = Mapping({
        'REFERENCE_FLAG_UNDEFINED_NON_LAZY': 0,
        'REFERENCE_FLAG_UNDEFINED_LAZY': 1,
        'REFERENCE_FLAG_DEFINED': 2,
        'REFERENCE_FLAG_PRIVATE_DEFINED': 3,
        'REFERENCE_FLAG_PRIVATE_UNDEFINED_NON_LAZY': 4,
        'REFERENCE_FLAG_PRIVATE_UNDEFINED_LAZY': 5,
    })

    REFERENCE_DYNAMICALLY = 0x0010
    N_NO_DEAD_STRIP = 0x0020
    N_DESC_DISCARDED = 0x0020  # TODO - ??? how is it used ???
    N_WEAK_REF = 0x0040
    N_WEAK_DEF = 0x0080
    N_REF_TO_WEAK = 0x0080
    N_ARM_THUMB_DEF = 0x0008
    N_SYMBOL_RESOLVER = 0x0100

    def validate(self, header):
        value = self._get_value(header)
        return self.REFERENCE_FLAGS.has_value(value & self.REFERENCE_TYPE)

    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            attrs = list()
            attrs.append(self.REFERENCE_FLAGS.key(value & self.REFERENCE_TYPE))
            if value & self.REFERENCE_DYNAMICALLY:
                attrs.append('REFERENCE_DYNAMICALLY')
            if value & self.N_NO_DEAD_STRIP:
                attrs.append('N_NO_DEAD_STRIP')
            if value & self.N_WEAK_REF:
                attrs.append('N_WEAK_REF')
            if value & self.N_WEAK_DEF:
                attrs.append('N_WEAK_DEF')
            return ','.join(attrs)

    def is_global(self, header):
        return self._get_value(header) in (0, 1, 2)

    def is_defined(self, header):
        return self._get_value(header) in (2, 3)

    def is_lazy(self, header):
        return self._get_value(header) in (1, 5)


class Nlist(IndexedHeader):
    ENDIAN = None
    FIELDS = (
        Field('n_strx', 'I'),
        NType('n_type', 'B'),
        NSect('n_sect', 'B'),
        NDesc('n_desc', 'h'),
        HexField('n_value', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.n_strx = None
        self.n_type = None
        self.n_sect = None
        self.n_desc = None
        self.n_value = None
        super(Nlist, self).__init__('nlist', bytes_, **kwargs)

    def is_global(self):
        return self.FIELDS[3].is_global(self)

    def is_defined(self):
        return self.FIELDS[3].is_defined(self)

    def is_lazy(self):
        return self.FIELDS[3].is_lazy(self)

    def type(self):
        return self.FIELDS[1].type(self)


class Nlist64(IndexedHeader):
    ENDIAN = None
    FIELDS = (
        Field('n_strx', 'I'),
        NType('n_type', 'B'),
        NSect('n_sect', 'B'),
        NDesc('n_desc', 'H'),
        HexField('n_value', 'Q'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.n_strx = None
        self.n_type = None
        self.n_sect = None
        self.n_desc = None
        self.n_value = None
        super(Nlist64, self).__init__('nlist64', bytes_, **kwargs)

    def is_global(self):
        return self.FIELDS[3].is_global(self)

    def is_defined(self):
        return self.FIELDS[3].is_defined(self)

    def is_lazy(self):
        return self.FIELDS[3].is_lazy(self)

    def type(self):
        return self.FIELDS[1].type(self)
