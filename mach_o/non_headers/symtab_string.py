from utils.header import ColorIndexedHeader, NonEncodingField


class SymtabString(ColorIndexedHeader):
    FIELDS = (
        NonEncodingField('offset'),
        NonEncodingField('string'),
    )

    def __init__(self, offset, s):
        self.offset = None
        self.string = None
        super(SymtabString, self).__init__('symtab_string', 'green', offset=offset, string=s)
