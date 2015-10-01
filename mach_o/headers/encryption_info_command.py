from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class EncryptionInfoCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_ENCRYPTION_INFO']: 'LC_ENCRYPTION_INFO'}),
        Field('cmdsize', 'I'),
        Field('cryptoff', 'I'),
        Field('cryptsize', 'I'),
        Field('cryptid', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.cryptoff = None
        self.cryptsize = None
        self.cryptid = None
        super(EncryptionInfoCommand, self).__init__('encryption_info_command', bytes_, **kwargs)


class EncryptionInfoCommand64(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_ENCRYPTION_INFO_64']: 'LC_ENCRYPTION_INFO_64'}),
        Field('cmdsize', 'I'),
        Field('cryptoff', 'I'),
        Field('cryptsize', 'I'),
        Field('cryptid', 'I'),
        Field('pad', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.cryptoff = None
        self.cryptsize = None
        self.cryptid = None
        self.pad = None
        super(EncryptionInfoCommand64, self).__init__('encryption_info_command_64', bytes_, **kwargs)
