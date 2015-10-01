from utils.header import Field, MagicField, HexField, NullTerminatedStringField
from mach_o.headers.load_command import LoadCommandCommand, LoadCommandHeader


class SegmentCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_SEGMENT']: 'LC_SEGMENT'}),
        Field('cmdsize', 'I'),
        NullTerminatedStringField('segname', '16s'),
        HexField('vmaddr', 'I'),
        Field('vmsize', 'I'),
        Field('fileoff', 'I'),
        Field('filesize', 'I'),
        Field('maxprot', 'I'),
        Field('initprot', 'I'),
        Field('nsects', 'I'),
        HexField('flags', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.segname = None
        self.vmaddr = None
        self.vmsize = None
        self.fileoff = None
        self.filesize = None
        self.maxprot = None
        self.initprot = None
        self.nsects = None
        self.flags = None
        super(SegmentCommand, self).__init__('segment_command', bytes_, **kwargs)


class SegmentCommand64(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_SEGMENT_64']: 'LC_SEGMENT_64'}),
        Field('cmdsize', 'I'),
        NullTerminatedStringField('segname', '16s'),
        HexField('vmaddr', 'Q'),
        Field('vmsize', 'Q'),
        Field('fileoff', 'Q'),
        Field('filesize', 'Q'),
        Field('maxprot', 'I'),
        Field('initprot', 'I'),
        Field('nsects', 'I'),
        HexField('flags', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.segname = None
        self.vmaddr = None
        self.vmsize = None
        self.fileoff = None
        self.filesize = None
        self.maxprot = None
        self.initprot = None
        self.nsects = None
        self.flags = None
        super(SegmentCommand64, self).__init__('segment_command_64', bytes_, **kwargs)
