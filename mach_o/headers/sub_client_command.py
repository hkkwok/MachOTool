from utils.header import MagicField, Field
from load_command import LoadCommandHeader, LoadCommandCommand


class SubClientCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_SUB_CLIENT']: 'LC_SUB_CLIENT'}),
        Field('cmdsize', 'I'),
        Field('client_offset', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.client_offset = None
        super(SubClientCommand, self).__init__(bytes_, **kwargs)
