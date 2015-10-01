from utils.header import MagicField, Field
from load_command import LoadCommandCommand, LoadCommandHeader


class UuidField(Field):
    def display(self, header):
        value = self._get_value(header)
        if self.mnemonic:
            return '%02x%02x%02x%02x-%02x%02x-%02x%02x-%02x%02x-%02x%02x%02x%02x%02x%02x' % \
                   tuple([ord(x) for x in value])
        else:
            return ''.join([hex(ord(x)) for x in value])


class UuidCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_UUID']: 'LC_UUID'}),
        Field('cmdsize', 'I'),
        UuidField('uuid', '16s'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.uuid = None
        super(UuidCommand, self).__init__('uuid_command', bytes_, **kwargs)
