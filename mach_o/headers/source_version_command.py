from utils.header import MagicField, Field
from load_command import LoadCommandCommand, LoadCommandHeader


class SourceVersionField(Field):
    def display(self, header):
        if self.mnemonic:
            value = self._get_value(header)
            a = (value >> 40) & 0xffffff
            b = (value >> 30) & 0x3ff
            c = (value >> 20) & 0x3ff
            d = (value >> 10) & 0x3ff
            e = value & 0x3ff
            return '%d.%d.%d.%d.%d' % (a, b, c, d, e)
        return super(SourceVersionField, self).display(header)


class SourceVersionCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_SOURCE_VERSION']: 'LC_SOURCE_VERSION'}),
        Field('cmdsize', 'I'),
        SourceVersionField('version', 'Q'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.version = None
        super(SourceVersionCommand, self).__init__('source_version_command', bytes_, **kwargs)
