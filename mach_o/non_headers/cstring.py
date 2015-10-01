from utils.header import ColorIndexedHeader, NonEncodingField


class Cstring(ColorIndexedHeader):
    ENDIAN = None
    FIELDS = (
        NonEncodingField('string'),
    )

    def __init__(self, s):
        super(Cstring, self).__init__('cstring', color='green', bold=False, string=s)
