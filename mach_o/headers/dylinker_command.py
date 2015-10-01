from utils.header import MagicField, Field
from load_command import LoadCommandCommand, LoadCommandHeader


class DylinkerCommand(LoadCommandHeader):
    ENDIAN = None
    FIELDS = (
        MagicField('cmd', 'I', {LoadCommandCommand.COMMANDS['LC_ID_DYLINKER']: 'LC_ID_DYLINKER',
                                LoadCommandCommand.COMMANDS['LC_LOAD_DYLINKER']: 'LC_LOAD_DYLINKER',
                                LoadCommandCommand.COMMANDS['LC_DYLD_ENVIRONMENT']: 'LC_DYLD_ENVIRONMENT'}),
        Field('cmdsize', 'I'),
        Field('name_offset', 'I'),
    )

    def __init__(self, bytes_=None, **kwargs):
        self.name_offset = None
        super(DylinkerCommand, self).__init__('dylinker_command', bytes_, **kwargs)
