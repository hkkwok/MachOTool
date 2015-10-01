from utils.header import MagicField, Field, UnixTimeField, VersionField
from load_command import LoadCommandCommand, LoadCommandHeader


class DylibCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I',
                   {LoadCommandCommand.COMMANDS['LC_LOAD_DYLIB']: 'LC_LOAD_DYLIB',
                    LoadCommandCommand.COMMANDS['LC_LOAD_WEAK_DYLIB']: 'LC_LOAD_WEAK_DYLIB',
                    LoadCommandCommand.COMMANDS['LC_ID_DYLIB']: 'LC_ID_DYLIB'}),
        Field('cmdsize', 'I'),
        Field('dylib_name_offset', 'I'),
        UnixTimeField('dylib_timestamp', 'I'),
        VersionField('dylib_current_version', 'I'),
        VersionField('dylib_compatiblity_version', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.dylib_name_offset = None
        self.dylib_timestamp = None
        self.dylib_current_version = None
        self.dylib_compatibility_version = None
        super(DylibCommand, self).__init__('dylib_command', bytes_, **kwargs)
