from utils.header import MagicField, Field
from utils.range import Range
from load_command import LoadCommandHeader, LoadCommandCommand
from section import Section, Section64


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

    def is_encrypted(self):
        return self.cryptid != 0

    def covers(self, section):
        assert isinstance(section, Section)
        return (Range(section.offset, section.offset + section.size) in
                Range(self.cryptoff, self.cryptoff + self.cryptsize))


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

    def is_encrypted(self):
        return self.cryptid != 0

    def covers(self, section):
        assert isinstance(section, Section64)
        return (Range(section.offset, section.offset + section.size) in
                Range(self.cryptoff, self.cryptoff + self.cryptsize))
