from utils.header import IndexedHeader, Field, HexField, NullTerminatedStringField


class Section(IndexedHeader):
    ENDIAN = None
    FIELDS = (
        NullTerminatedStringField('sectname', '16s'),
        NullTerminatedStringField('segname', '16s'),
        HexField('addr', 'I'),
        Field('size', 'I'),
        Field('offset', 'I'),
        Field('align', 'I'),
        Field('reloff', 'I'),
        Field('nreloc', 'I'),
        HexField('flags', 'I'),
        Field('reserved1', 'I'),
        Field('reserved2', 'I'),
    )

    NEXT_INDEX = 1

    def __init__(self, bytes_=None, **kwargs):
        self.sectname = None
        self.segname = None
        self.addr = None
        self.size = None
        self.offset = None
        self.align = None
        self.reloff = None
        self.nreloc = None
        self.flags = None
        self.reserved1 = None
        self.reserved2 = None
        super(Section, self).__init__('section', bytes_, **kwargs)


class Section64(IndexedHeader):
    ENDIAN = None
    FIELDS = (
        NullTerminatedStringField('sectname', '16s'),
        NullTerminatedStringField('segname', '16s'),
        HexField('addr', 'Q'),
        Field('size', 'Q'),
        Field('offset', 'I'),
        Field('align', 'I'),
        Field('reloff', 'I'),
        Field('nreloc', 'I'),
        HexField('flags', 'I'),
        Field('reserved1', 'I'),
        Field('reserved2', 'I'),
        Field('reserved3', 'I'),
    )

    NEXT_INDEX = 1

    def __init__(self, bytes_=None, **kwargs):
        self.sectname = None
        self.segname = None
        self.addr = None
        self.size = None
        self.offset = None
        self.align = None
        self.reloff = None
        self.nreloc = None
        self.flags = None
        self.reserved1 = None
        self.reserved2 = None
        super(Section64, self).__init__('section_64', bytes_, **kwargs)
