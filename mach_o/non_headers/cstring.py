from utils.header import ColorIndexedHeader, NonEncodingField


class NullTerminatedString(ColorIndexedHeader):
    ENDIAN = None
    FIELDS = (
        NonEncodingField('string'),
    )

    def __init__(self, name, s):
        super(NullTerminatedString, self).__init__(name, color='green', bold=False, string=s)


class Cstring(NullTerminatedString):
    def __init__(self, s):
        super(Cstring, self).__init__('cstring', s)


class ObjCMethodName(NullTerminatedString):
    def __init__(self, s):
        super(ObjCMethodName, self).__init__('objc_methname', s)
