from utils.header import MagicField, Field, VersionField
from load_command import LoadCommandCommand, LoadCommandHeader


class VersionMinCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I',
                   {LoadCommandCommand.COMMANDS['LC_VERSION_MIN_MACOSX']: 'LC_VERSION_MIN_MACOSX',
                    LoadCommandCommand.COMMANDS['LC_VERSION_MIN_IPHONEOS']: 'LC_VERSION_MIN_IPHONEOS'}),
        Field('cmdsize', 'I'),
        VersionField('version', 'I'),
        VersionField('sdk', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.version = None
        self.sdk = None
        super(VersionMinCommand, self).__init__('version_min_command', bytes_, **kwargs)
