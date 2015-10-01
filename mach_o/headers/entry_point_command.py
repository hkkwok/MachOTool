from utils.header import MagicField, Field
from load_command import LoadCommandCommand, LoadCommandHeader


class EntryPointCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_MAIN']: 'LC_MAIN'}),
        Field('cmdsize', 'I'),
        Field('entryoff', 'I'),
        Field('stacksize', 'Q'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.entryoff = None
        self.stacksize = None
        super(EntryPointCommand, self).__init__('entry_point_command', bytes_, **kwargs)
